/* S.A.G.E. care dashboard: small progressive enhancements. The pages work without this file. */
(function () {
  "use strict";

  /* --- busy buttons: show what is happening and stop double presses ------- */
  document.addEventListener("submit", function (e) {
    var form = e.target;
    if (!form.hasAttribute || !form.hasAttribute("data-busy")) return;
    var button = form.querySelector("[data-busy-label]");
    if (!button) return;
    if (form.dataset.submitted) { e.preventDefault(); return; }
    form.dataset.submitted = "1";
    button.setAttribute("aria-busy", "true");
    var label = button.querySelector("span") || button;
    label.textContent = button.getAttribute("data-busy-label");
  });

  /* --- "Show the password" ----------------------------------------------- */
  var showRow = document.getElementById("show-password-row");
  var showBox = document.getElementById("show-password");
  var pw = document.getElementById("password");
  if (showRow && showBox && pw) {
    showRow.hidden = false;
    showBox.addEventListener("change", function () { pw.type = showBox.checked ? "text" : "password"; });
  }

  /* --- live updates ------------------------------------------------------ */
  var main = document.querySelector("main[data-live]");
  if (!main) return;

  var indicator = document.getElementById("live-indicator");
  var label = indicator.querySelector(".live-label");
  var updated = document.getElementById("live-updated");
  var announcer = document.getElementById("live-announcer");
  var signedOutNotice = document.getElementById("signed-out-notice");
  var streamUrl = main.dataset.streamUrl;
  var revisionUrl = main.dataset.revisionUrl;
  var pollMs = parseInt(main.dataset.pollMs, 10) || 10000;
  var revision = parseInt(main.dataset.revision, 10);

  var source = null, pollTimer = null, retryStreamTimer = null, reconnectTimer = null;
  var failures = 0, refreshing = false, again = false, stopped = false;

  indicator.hidden = false;

  function setState(state, text) {
    if (stopped) return;
    indicator.dataset.state = state;
    label.textContent = text;
  }
  function showReconnecting() {
    // Short blips (a stream ending normally and reopening) should not flicker.
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(function () { reconnectTimer = null; setState("reconnecting", "Reconnecting…"); }, 1500);
  }
  function showLive() {
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
    setState("live", "Live");
  }
  function stamp(time) { updated.textContent = "Updated " + time; }

  function signedOut() {
    stopAll();
    setState("offline", "Signed out");
    stopped = true;
    signedOutNotice.hidden = false;
  }
  function stopAll() {
    if (source) { source.close(); source = null; }
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    if (retryStreamTimer) { clearTimeout(retryStreamTimer); retryStreamTimer = null; }
  }

  function openAlerts(root) {
    var el = root.querySelector("[data-open-alerts]");
    return el ? parseInt(el.getAttribute("data-open-alerts"), 10) : 0;
  }

  /* Fetch this same page again and swap in the parts that can change. */
  function refresh(time) {
    if (refreshing) { again = true; return; }
    refreshing = true;
    var before = openAlerts(document);
    fetch(window.location.href, { headers: { "X-Live-Refresh": "1" }, credentials: "same-origin" })
      .then(function (r) {
        if (r.status === 401) { signedOut(); throw null; }
        if (!r.ok) throw new Error("refresh failed");
        return r.text();
      })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var focusedId = document.activeElement && document.activeElement.id;
        document.querySelectorAll("[data-live-region]").forEach(function (el) {
          var fresh = doc.getElementById(el.id);
          if (fresh) el.replaceWith(document.importNode(fresh, true));
        });
        // Keep keyboard focus where it was, if that control still exists.
        var refocus = focusedId && document.getElementById(focusedId);
        if (refocus) refocus.focus();
        var after = openAlerts(document);
        var summary = document.querySelector("[data-announce]");
        if (after > before && summary) {
          announcer.textContent = "New update. " + summary.getAttribute("data-announce");
        }
        main.classList.remove("is-updating");
        stamp(time || clockNow());
        showLive();
      })
      .catch(function (err) { if (err !== null) showReconnecting(); })
      .then(function () {
        refreshing = false;
        if (again && !stopped) { again = false; refresh(); }
      });
  }

  function clockNow() {
    var d = new Date(), h = d.getHours() % 12 || 12, m = ("0" + d.getMinutes()).slice(-2);
    return h + ":" + m + " " + (d.getHours() < 12 ? "am" : "pm");
  }

  function handle(data) {
    if (data.revision !== revision) {
      revision = data.revision;
      main.classList.add("is-updating");
      refresh(data.time);
    } else {
      stamp(data.time);
      showLive();
    }
  }

  /* Server-Sent Events first. */
  function connectStream() {
    if (stopped) return;
    if (!("EventSource" in window)) { startPolling(); return; }
    source = new EventSource(streamUrl);
    source.addEventListener("open", function () { failures = 0; showLive(); });
    source.addEventListener("update", function (e) { handle(JSON.parse(e.data)); });
    source.addEventListener("ping", function (e) { handle(JSON.parse(e.data)); });
    source.addEventListener("error", function () {
      failures += 1;
      showReconnecting();
      if (failures >= 3 || source.readyState === 2) {
        // The stream keeps failing: fall back to simple polling, and try
        // the stream again a little later. A 401 is found by the poll.
        source.close();
        source = null;
        startPolling();
      }
    });
  }

  /* Simple polling as a fallback. */
  function poll() {
    fetch(revisionUrl, { headers: { "X-Live-Refresh": "1" }, credentials: "same-origin" })
      .then(function (r) {
        if (r.status === 401) { signedOut(); throw null; }
        if (!r.ok) throw new Error("poll failed");
        return r.json();
      })
      .then(handle)
      .catch(function (err) { if (err !== null) showReconnecting(); });
  }
  function startPolling() {
    if (stopped || pollTimer) return;
    poll();
    pollTimer = setInterval(poll, pollMs);
    if ("EventSource" in window) {
      retryStreamTimer = setTimeout(function () {
        clearInterval(pollTimer); pollTimer = null; failures = 0; connectStream();
      }, Math.max(pollMs * 3, 30000));
    }
  }

  window.addEventListener("online", function () { if (!stopped && !source) { stopAll(); failures = 0; connectStream(); } });
  connectStream();
})();
