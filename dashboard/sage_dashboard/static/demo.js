/* Live demo page. Only reads from the server; it never controls processing. */
(function () {
  "use strict";
  var root = document.getElementById("demo");
  if (!root) return;

  var STATUS_MS = 1000, EVENTS_MS = 1500, MAX_ROWS = 300;
  var statusUrl = root.dataset.statusUrl, eventsUrl = root.dataset.eventsUrl, videoUrl = root.dataset.videoUrl;
  var video = document.getElementById("demo-video");
  var logBody = document.getElementById("demo-log-body");
  var logEmpty = document.getElementById("demo-log-empty");
  var stateEl = document.getElementById("demo-state");
  var lastEventId = 0, stopped = false, videoRunning = false, videoRetry = null;

  /* --- tabs (switching only changes what is shown) ---------------------- */
  var tabs = Array.prototype.slice.call(root.querySelectorAll('[role="tab"]'));
  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
    });
    if (focus) tab.focus();
    try { history.replaceState(null, "", "#" + tab.id.replace("tab-", "")); } catch (e) { /* ignore */ }
    updateVideo();
  }
  tabs.forEach(function (tab, i) {
    tab.addEventListener("click", function () { select(tab, false); });
    tab.addEventListener("keydown", function (e) {
      var next = null;
      if (e.key === "ArrowRight") next = tabs[(i + 1) % tabs.length];
      if (e.key === "ArrowLeft") next = tabs[(i - 1 + tabs.length) % tabs.length];
      if (e.key === "Home") next = tabs[0];
      if (e.key === "End") next = tabs[tabs.length - 1];
      if (next) { e.preventDefault(); select(next, true); }
    });
  });
  var initial = document.getElementById("tab-" + (location.hash || "#live").slice(1)) || tabs[0];

  /* --- video: connect only while the Live tab is shown ------------------- */
  // Disconnecting just stops this browser receiving frames. The server keeps
  // processing, so coming back shows the current frame, not the start.
  function liveShown() { return !document.getElementById("panel-live").hidden; }
  function updateVideo() {
    var want = liveShown() && videoRunning && !stopped;
    if (want && !video.getAttribute("src")) {
      video.src = videoUrl + "?t=" + Date.now();
    } else if (!want && video.getAttribute("src")) {
      video.removeAttribute("src");
    }
  }
  video.addEventListener("error", function () {
    video.removeAttribute("src");
    if (videoRetry) clearTimeout(videoRetry);
    videoRetry = setTimeout(updateVideo, 2000);
  });

  /* --- status ------------------------------------------------------------- */
  function setField(name, value) {
    root.querySelectorAll('[data-field="' + name + '"]').forEach(function (el) { el.textContent = value; });
  }
  var STATE_LABELS = { running: "Running", loading: "Loading models…", stopped: "Stopped",
                       error: "Stopped (problem)", not_started: "Not started" };
  function yesNo(v, yes, no) { return v ? yes : no; }

  function showStatus(s) {
    var state = s.state || "unknown";
    stateEl.dataset.state = state;
    setField("state_label", STATE_LABELS[state] || state);
    document.getElementById("demo-not-running").hidden = state !== "not_started";
    document.getElementById("demo-error").hidden = state !== "error";
    setField("error", s.error || "");
    var c = s.components || {};
    var loaded = state === "running" || state === "loading";
    setField("pose_label", c.pose ? "Running" : (state === "loading" ? "Loading…" : "Not running"));
    setField("heuristic_label", c.heuristic ? (state === "running" ? "Running" : "Loaded") : (state === "loading" ? "Loading…" : "Not running"));
    setField("lstm_label", c.lstm ? "Loaded and running" : (loaded && c.pose ? "Not available (heuristic only)" : "–"));
    setField("objects_label", c.object_detection ? "Running (" + c.object_model + ")" : (loaded && c.pose ? "Not available" : "–"));
    showGait(s.gait || {}, loaded && c.pose);
    setField("video", s.video || "–");
    setField("started_label", s.started_at ? new Date(s.started_at).toLocaleTimeString() : "–");
    ["frames_processed", "loop_number", "frame_in_clip", "fall_frames_in_window", "people_in_view",
     "total_events", "server_time", "alert_window", "alert_min_hits"].forEach(function (k) { if (s[k] !== undefined && s[k] !== null) setField(k, s[k]); });
    setField("frames_in_clip", s.frames_in_clip || "?");
    setField("processing_fps", s.processing_fps != null ? s.processing_fps.toFixed(1) : "–");
    setField("video_fps", s.video_fps != null ? s.video_fps : "–");
    setField("last_frame_ms", s.last_frame_ms != null ? s.last_frame_ms : "–");
    var t = s.video_time || 0;
    setField("video_clock", Math.floor(t / 60) + ":" + ("0" + (t % 60).toFixed(1)).slice(-4));
    setField("posture", s.posture || "–");
    setField("fall_signal_label", s.posture ? yesNo(s.fall_signal, "Yes", "No") : "–");
    setField("alarm_label", s.posture ? yesNo(s.alarm_active, "ACTIVE", "Not active") : "–");
    var counts = s.counts || {};
    ["fall_alert", "possible_fall", "person_detected", "person_left", "gait_risk"].forEach(function (k) {
      setField("count_" + k, counts[k] || 0);
    });
    var latest = s.latest_event;
    setField("latest_event_text", latest ? latest.label + " at " + latest.seconds + " (clip " + latest.video_time + ")" : "None yet");
    var list = document.getElementById("demo-objects");
    var objs = s.objects || [];
    list.innerHTML = "";
    if (!objs.length) {
      var li = document.createElement("li"); li.className = "muted"; li.textContent = "None"; list.appendChild(li);
    }
    objs.forEach(function (o) {
      var li = document.createElement("li");
      li.textContent = o["class"] + " " + Math.round(o.confidence * 100) + "%";
      list.appendChild(li);
    });
    videoRunning = state === "running";
    updateVideo();
  }

  function showGait(g, started) {
    if (!g.running) {
      var off = g.error ? "Not available (" + g.error + ")" : (started ? "Off" : "–");
      ["gait_label", "gait_component_label"].forEach(function (k) { setField(k, off); });
      setField("gait_window_label", "–");
      setField("gait_baseline_label", "–");
      return;
    }
    var now;
    if (!g.assessments) now = "Warming up (" + g.frames_buffered + " of " + g.window_frames + " frames)";
    else if (g.risk_score == null) now = "Not measurable in this window";
    else now = g.risk_score.toFixed(2) + " (" + g.band + ")";
    setField("gait_label", now);
    setField("gait_component_label", g.error ? "Running (last problem: " + g.error + ")" : "Running");
    setField("gait_window_label", g.frames_buffered + " of " + g.window_frames + ", new score every " + g.reassess_every + " frames");
    setField("gait_baseline_label", g.baseline_mode ? "Set (" + g.baseline_mode + ")" : "Waiting for steady standing");
  }

  /* --- events --------------------------------------------------------------- */
  function detailText(e) {
    var d = e.details || {}, parts = [];
    if (d.risk_score != null) parts.push("risk " + d.risk_score.toFixed(2) + " (" + d.band + ")");
    if (d.signals) parts.push(Object.keys(d.signals).join(", ") || "no signals");
    if (d.posture) parts.push("posture " + d.posture);
    if (d.heuristic_labels) parts.push(d.heuristic_labels);
    if (d.fall_frames_in_window != null) parts.push(d.fall_frames_in_window + "/" + d.window + " fall frames");
    if (d.people_in_view != null) parts.push(d.people_in_view + " in view");
    if (d.seconds_in_view != null) parts.push("in view " + d.seconds_in_view + " s");
    if (d.gait_risk_score != null) parts.push("gait risk " + d.gait_risk_score.toFixed(2));
    return parts.join(" · ");
  }
  function addRows(events) {
    // events arrive newest first
    for (var i = events.length - 1; i >= 0; i--) {
      var e = events[i];
      var tr = document.createElement("tr");
      tr.className = "event-row demo-event demo-" + e.type;
      tr.dataset.type = e.type;
      tr.dataset.eventId = e.id;
      var cells = [
        ["Time", e.seconds],
        ["Event", e.label],
        ["Confidence", e.confidence_percent != null ? e.confidence_percent + "%" : "–"],
        ["Clip position", e.video_time + " · frame " + e.frame + " · pass " + e.loop],
        ["Details", detailText(e) || "–"]
      ];
      cells.forEach(function (c) {
        var td = document.createElement("td");
        td.dataset.label = c[0];
        td.textContent = c[1];
        tr.appendChild(td);
      });
      logBody.insertBefore(tr, logBody.firstChild);
      lastEventId = Math.max(lastEventId, e.id);
    }
    while (logBody.children.length > MAX_ROWS) logBody.removeChild(logBody.lastChild);
    logEmpty.hidden = logBody.children.length > 0;
  }

  /* --- polling ---------------------------------------------------------------- */
  function get(url) {
    return fetch(url, { headers: { "X-Live-Refresh": "1" }, credentials: "same-origin" }).then(function (r) {
      if (r.status === 401) { signedOut(); throw null; }
      if (!r.ok) throw new Error("request failed");
      return r.json();
    });
  }
  function signedOut() {
    stopped = true;
    document.getElementById("demo-signed-out").hidden = false;
    updateVideo();
  }
  function pollStatus() {
    if (stopped) return;
    get(statusUrl).then(showStatus).catch(function () {}).then(function () {
      if (!stopped) setTimeout(pollStatus, STATUS_MS);
    });
  }
  function pollEvents() {
    if (stopped) return;
    get(eventsUrl + "?after=" + lastEventId).then(function (d) { addRows(d.events || []); })
      .catch(function () {}).then(function () { if (!stopped) setTimeout(pollEvents, EVENTS_MS); });
  }

  select(initial, false);
  pollStatus();
  pollEvents();
})();
