"""Background video processing for the live demo.

One worker thread, started once when the server starts (`manage.py demo`),
reads a local video file frame by frame, loops it forever, and for every
frame runs the EXISTING S.A.G.E. pipeline:

    MediaPipe pose -> heuristic posture/fall (OR the LSTM, if it loads)
                   -> GAIT streaming risk score (src/gait), in parallel
                   -> YOLO object detection on the same frame

Nothing here re-implements detection. Model loading, the per-frame
classification and the overlay drawing are the functions from
realtime_fall_detection.py and src/posture/pipeline_utils.py, called as
they are. The only logic reproduced here is that script's fall-alert
debounce (same constants, same rule), because its `run()` loop cannot hand
frames to a web page or loop a file.

GAIT is wired the way realtime_fall_detection.py wired it at commit
c3bd40a (the working copy of that file has since dropped it): the
StreamingGaitRiskAssessor and TorsoBaselineCalibrator from
src/gait/gait_stream.py, fed the same pose rows plus MediaPipe's 3D world
landmarks, with the same window, cadence and calibration length. It is a
separate signal: it never feeds the fall alert, and an error in it never
stops fall detection.

The dashboard never controls this thread. Pages only read from it: the
latest annotated frame (kept in memory, never written to disk), a status
snapshot, and the events it stored in the database. Opening, refreshing,
switching tabs or closing pages does not start, pause or restart it.

Timing: every frame of the clip is processed, using the clip's own
timestamps, so the heuristic and LSTM see exactly what the offline
evaluation sees. If the computer is faster than the clip, the loop waits
so playback runs at normal speed; if it is slower, playback is slowed down
rather than frames being skipped (skipping would change what the LSTM sees).
"""

import json
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from . import live, queries
from .sources import PipelineSource, default_severity, ingest

REPO_ROOT = Path(__file__).resolve().parents[2]

# Same values as realtime_fall_detection.py (ALERT_WINDOW, ALERT_MIN_HITS,
# ALERT_HOLD_SECONDS, HISTORY_CAP). Read from that module when it loads;
# these copies only serve the tests, which never import the heavy models.
ALERT_WINDOW = 12
ALERT_MIN_HITS = 4
ALERT_HOLD_SECONDS = 5.0
HISTORY_CAP = 320

# A person must be missing from YOLO's output for this long (clip time)
# before "person_left" is logged. Stops a box flickering for a frame or two
# from producing a stream of left/detected pairs.
PERSON_ABSENT_SECONDS = 2.0
PERSON_CLASS = "person"

# GAIT settings realtime_fall_detection.py used (GAIT_REASSESS_EVERY_N_FRAMES,
# GAIT_MIN_CALIBRATION_FRAMES at c3bd40a). The window length is read from
# StreamingGaitRiskAssessor's own default, as that script did.
GAIT_REASSESS_EVERY_N_FRAMES = 15
GAIT_MIN_CALIBRATION_FRAMES = 60


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _available_signals(gait_result):
    """{signal name: risk contribution} for the gait signals this window could measure."""
    return {s["name"]: round(float(s["risk_contribution"]), 3)
            for s in gait_result.get("signals", [])
            if s.get("available") and s.get("risk_contribution") is not None}


def gait_row(row, world_landmarks, landmark_count):
    """The pose row the gait assessor reads: `row` plus MediaPipe's 3D world
    landmarks as "world_keypoints" (flat x, y, z per joint).

    This is the plumbing build_pose_row(world_landmarks=...) did at c3bd40a.
    A joint the 2D row already dropped as not visible is dropped in 3D too.
    Returned as a copy, so the row the fall detection sees is unchanged.
    """
    out = dict(row)
    if world_landmarks:
        nan = float("nan")
        world = [float(c) if c is not None else nan for xyz in world_landmarks[:landmark_count] for c in xyz]
        world += [nan] * (landmark_count * 3 - len(world))
        keypoints = row.get("keypoints") or []
        for i in range(landmark_count):
            if 2 * i >= len(keypoints) or keypoints[2 * i] != keypoints[2 * i]:  # NaN: not trusted
                world[3 * i:3 * i + 3] = [nan, nan, nan]
        out["world_keypoints"] = world
    return out


def _draw_gait(frame, gait_status):
    """The gait line of the overlay, as realtime_fall_detection._draw_gait drew it at c3bd40a."""
    import cv2
    white, amber = (255, 255, 255), (0, 165, 255)
    if not gait_status.get("running"):
        return
    if gait_status["assessments"] == 0:
        note = "" if gait_status["baseline_mode"] else " (baseline pending)"
        text, color = f"Gait: warming up{note}", white
    elif gait_status["risk_score"] is None:
        text, color = "Gait risk: n/a this window", white
    else:
        score = gait_status["risk_score"]
        note = f"  [baseline: {gait_status['baseline_mode']}]" if gait_status["baseline_mode"] else ""
        text, color = f"Gait risk: {score:.2f}{note}", amber if score >= 0.6 else white
    cv2.putText(frame, text, (12, 142), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)


class EventTracker:
    """Turns per-frame pipeline output into a small number of events.

    - fall_alert: the realtime script's debounce, unchanged: at least
      `min_hits` fall-flagged frames in the last `window` frames raises the
      alert, which then stays latched for `hold` seconds and only re-arms
      once no frame in the window is flagged.
    - possible_fall: the first fall-flagged frame of a burst while no alert
      is active. One per burst; a burst ends when the window is clear again.
    - person_detected / person_left: YOLO "person" boxes appearing, and then
      being absent for PERSON_ABSENT_SECONDS.
    - gait_risk: the first gait risk score of a pass, then each time the
      score moves into a different band (low / medium / high, the same
      cut-offs the caregiver pages use). Fresh scores arrive every 15
      frames; logging each one would bury the other events.

    Detection thresholds are not touched: this only decides how often to log.
    """

    def __init__(self, window=ALERT_WINDOW, min_hits=ALERT_MIN_HITS, hold=ALERT_HOLD_SECONDS,
                 person_absent=PERSON_ABSENT_SECONDS, person_class=PERSON_CLASS):
        self.window, self.min_hits, self.hold = window, min_hits, hold
        self.person_absent, self.person_class = person_absent, person_class
        self.reset()

    def reset(self):
        self.flags = deque(maxlen=self.window)
        self.alarm_active = False
        self.alarm_until = 0.0
        self.burst_open = False
        self.person_in_view = False
        self.person_since = None
        self.last_person_t = None
        self.hits = 0
        self.gait_score = None
        self.gait_band = None

    def update(self, t, fall_now, confidence=None, posture=None, labels="", objects=(), gait=None):
        events = []
        if gait is not None:  # a fresh GaitRiskAssessor.assess_risk() result
            score = gait.get("risk_score")
            self.gait_score = None if score is None else float(score)
            if self.gait_score is not None:
                band = default_severity("gait_risk", self.gait_score)
                if band != self.gait_band:
                    self.gait_band = band
                    events.append({"type": "gait_risk", "confidence": None,
                                   "details": {"risk_score": round(self.gait_score, 3), "band": band,
                                               "signals": _available_signals(gait)}})


        people = [o for o in objects if o.get("class") == self.person_class]
        if people:
            self.last_person_t = t
            if not self.person_in_view:
                self.person_in_view, self.person_since = True, t
                events.append({"type": "person_detected",
                               "confidence": max(o["confidence"] for o in people),
                               "details": {"people_in_view": len(people)}})
        elif self.person_in_view and t - self.last_person_t >= self.person_absent:
            events.append({"type": "person_left", "confidence": None,
                           "details": {"seconds_in_view": round(self.last_person_t - self.person_since, 1)}})
            self.person_in_view = False

        self.flags.append(1 if fall_now else 0)
        hits = sum(self.flags)
        # gait_risk_score is context only, as in realtime_fall_detection.py's
        # alert record; it never decides whether an alert fires.
        fall_details = {"posture": posture, "heuristic_labels": labels,
                        "fall_frames_in_window": hits, "window": self.window,
                        "gait_risk_score": None if self.gait_score is None else round(self.gait_score, 3)}
        if fall_now and not self.burst_open:
            self.burst_open = True
            if not self.alarm_active and hits < self.min_hits:
                events.append({"type": "possible_fall", "confidence": confidence, "details": fall_details})
        if not self.alarm_active and hits >= self.min_hits:
            self.alarm_active = True
            self.alarm_until = t + self.hold
            events.append({"type": "fall_alert", "confidence": confidence, "details": fall_details})
        elif self.alarm_active and t >= self.alarm_until and hits == 0:
            self.alarm_active = False
        if hits == 0:
            self.burst_open = False
        self.hits = hits
        return events


class SagePipeline:
    """The existing S.A.G.E. models, loaded once and run frame by frame."""

    def __init__(self, use_lstm=True, use_objects=True, object_model=None,
                 object_conf=0.25, object_imgsz=320, use_gait=True):
        self.use_lstm, self.use_objects, self.use_gait = use_lstm, use_objects, use_gait
        self.object_model, self.object_conf, self.object_imgsz = object_model, object_conf, object_imgsz
        self.rt = None
        self.pose = self.lstm = self.objects = None
        self.previous_rows = []
        self.gait_stream = self.gait_window = None
        self.gait = self.calibrator = None
        self.gait_error = None
        self.latest_gait = None
        self.gait_frames = self.gait_assessments = 0

    def load(self):
        # Imported here, not at the top: these libraries take a long time to
        # load and the web pages must not wait for them.
        import sys
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        import realtime_fall_detection as rt
        from src.posture import pipeline_utils
        self.rt, self.pu = rt, pipeline_utils
        self.pose = rt._make_detector()
        self.lstm = rt._load_lstm(self.use_lstm)
        model = Path(self.object_model) if self.object_model else rt.DEFAULT_OBJECT_MODEL_PATH
        self.object_model = model
        self.objects = rt._load_object_detector(self.use_objects, model, self.object_conf, self.object_imgsz)
        if self.use_gait:
            # Like the other optional parts, a gait failure must not stop fall detection.
            try:
                import inspect
                from src.gait import gait_stream
                self.gait_stream = gait_stream
                self.gait_window = inspect.signature(
                    gait_stream.StreamingGaitRiskAssessor.__init__).parameters["window_frames"].default
                self._new_gait_session()
            except Exception as exc:
                self.gait = self.calibrator = None
                self.gait_error = f"could not load: {type(exc).__name__}: {exc}"

    def _new_gait_session(self):
        # gait_stream asks for fresh instances for a new session rather than reset().
        self.gait = self.gait_stream.StreamingGaitRiskAssessor(
            window_frames=self.gait_window, reassess_every_n_frames=GAIT_REASSESS_EVERY_N_FRAMES)
        self.calibrator = self.gait_stream.TorsoBaselineCalibrator(min_run_frames=GAIT_MIN_CALIBRATION_FRAMES)
        self.latest_gait = None
        self.gait_frames = self.gait_assessments = 0

    @property
    def gait_status(self):
        if self.gait is None:
            return {"running": False, "error": self.gait_error}
        latest = self.latest_gait
        score = None if latest is None or latest.get("risk_score") is None else float(latest["risk_score"])
        return {"running": True, "error": self.gait_error, "window_frames": self.gait_window,
                "frames_buffered": min(self.gait_frames, self.gait_window),
                "reassess_every": GAIT_REASSESS_EVERY_N_FRAMES,
                "baseline_mode": self.calibrator.baseline_mode,
                "assessments": self.gait_assessments, "risk_score": score,
                "band": None if score is None else default_severity("gait_risk", score),
                "signals": _available_signals(latest) if latest else {}}

    @property
    def alert_settings(self):
        rt = self.rt
        return {"window": rt.ALERT_WINDOW, "min_hits": rt.ALERT_MIN_HITS, "hold": rt.ALERT_HOLD_SECONDS}

    @property
    def components(self):
        return {"pose": self.pose is not None,
                "heuristic": self.pose is not None,
                "lstm": self.lstm is not None,
                "object_detection": self.objects is not None,
                "object_model": Path(self.object_model).name if self.object_model else None,
                "gait": self.gait is not None}

    def reset(self):
        """A new pass through the clip is a new session (no motion across the jump)."""
        self.pu.reset_session_state()
        self.previous_rows = []
        if self.gait is not None:
            self._new_gait_session()

    def process(self, frame, stream_seconds, frame_no):
        import cv2
        import mediapipe as mp
        pu = self.pu
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                                            int(stream_seconds * 1000))
        landmarks, visibility, world_landmarks = [], [], []
        if result.pose_landmarks:
            landmarks = [(lm.x, lm.y) for lm in result.pose_landmarks[0]]
            visibility = [lm.visibility for lm in result.pose_landmarks[0]]
        if result.pose_world_landmarks:
            # Computed by the same detect_for_video() call; only gait reads it.
            world_landmarks = [(lm.x, lm.y, lm.z) for lm in result.pose_world_landmarks[0]]
        row = pu.build_pose_row(timestamp=str(stream_seconds), frame=frame_no, landmarks=landmarks,
                                visibility=visibility or None, min_visibility=pu.MIN_LANDMARK_VISIBILITY)
        out = pu.classify_posture_and_fall(row, previous_rows=self.previous_rows, lstm_classifier=self.lstm)
        row.update(out)
        self.previous_rows.append(row)
        if len(self.previous_rows) > self.rt.HISTORY_CAP:
            self.previous_rows = self.previous_rows[-self.rt.HISTORY_CAP:]
        posture, fall_now = out.get("posture_label", "Unknown"), bool(out.get("fall_detected", False))
        gait = self._push_gait(gait_row(row, world_landmarks, pu.LANDMARK_COUNT), posture, fall_now, frame_no)
        objects = self.objects.detect(frame) if self.objects is not None else []
        return {"posture": posture, "fall_now": fall_now,
                "confidence": float(out.get("confidence", 0.0) or 0.0),
                "labels": out.get("other_labels", "") or "",
                "landmarks": landmarks, "visibility": visibility, "objects": objects, "gait": gait}

    def _push_gait(self, row, posture, fall_now, frame_no):
        """Feed one frame to gait, after the fall decision. Returns a fresh result or None."""
        if self.gait is None:
            return None
        try:
            if not self.calibrator.is_calibrated and self.calibrator.observe(row, posture, fall_now):
                self.gait.set_torso_baseline(self.calibrator.baseline)
            self.gait_frames += 1
            result = self.gait.push_frame(row)
        except Exception as exc:  # reported on the status page; fall detection carries on
            self.gait_error = f"frame {frame_no}: {type(exc).__name__}: {exc}"
            return None
        if result is not None:
            self.latest_gait = result
            self.gait_assessments += 1
        return result

    def annotate(self, frame, res, alarm_active, fps, hits, window):
        rt = self.rt
        rt._draw_skeleton(frame, res["landmarks"], res["visibility"], self.pu.MIN_LANDMARK_VISIBILITY)
        rt._draw_objects(frame, res["objects"])
        rt._draw_overlay(frame, res["posture"], res["fall_now"], alarm_active, fps, hits, window)
        _draw_gait(frame, self.gait_status)

    def close(self):
        if self.pose is not None:
            self.pose.close()


class VideoProcessingService:
    """Runs the pipeline over a looping video in one background thread."""

    def __init__(self, video_path, db_path, pipeline, patient_external_id=None,
                 max_width=960, jpeg_quality=75, pace_to_video=True):
        self.video_path = Path(video_path)
        self.db_path = db_path
        self.pipeline = pipeline
        self.patient_external_id = patient_external_id
        self.max_width, self.jpeg_quality, self.pace_to_video = max_width, jpeg_quality, pace_to_video
        self._stop = threading.Event()
        self._thread = None
        self._lock = threading.Lock()
        self._frame_ready = threading.Condition()
        self._jpeg, self._frame_seq = None, 0
        self._state = {
            "state": "stopped", "error": None, "video": self.video_path.name,
            "started_at": None, "frames_processed": 0, "processing_fps": None, "video_fps": None,
            "frame_in_clip": 0, "frames_in_clip": None, "video_time": 0.0, "loop_number": 0,
            "posture": None, "fall_signal": False, "alarm_active": False, "fall_frames_in_window": 0,
            "people_in_view": 0, "objects": [], "components": {}, "events_logged": 0,
            "last_frame_ms": None, "alert_window": None, "alert_min_hits": None,
            "gait": {"running": False, "error": None},
        }

    # --- lifecycle ---------------------------------------------------------------

    def start(self):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, name="sage-video-processing", daemon=True)
            self._thread.start()
            return True

    def stop(self, timeout=10):
        self._stop.set()
        with self._frame_ready:
            self._frame_ready.notify_all()
        if self._thread is not None:
            self._thread.join(timeout)

    @property
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    # --- what the pages read ---------------------------------------------------------

    def status(self):
        with self._lock:
            snapshot = json.loads(json.dumps(self._state))
        if snapshot["state"] == "running" and not self.is_running:
            snapshot["state"] = "stopped"
        return snapshot

    def wait_for_frame(self, after_seq, timeout=5.0):
        """Return (seq, jpeg) for a frame newer than `after_seq`, or the current one on timeout."""
        with self._frame_ready:
            if self._frame_seq <= after_seq and not self._stop.is_set():
                self._frame_ready.wait(timeout)
            return self._frame_seq, self._jpeg

    # --- the worker -------------------------------------------------------------------

    def _set(self, **values):
        with self._lock:
            self._state.update(values)

    def _run(self):
        import cv2
        conn = None
        cap = None
        try:
            self._set(state="loading", error=None, started_at=_now_iso())
            self.pipeline.load()
            settings = self.pipeline.alert_settings
            tracker = EventTracker(settings["window"], settings["min_hits"], settings["hold"])
            self._set(components=self.pipeline.components, alert_window=settings["window"],
                      alert_min_hits=settings["min_hits"], gait=self.pipeline.gait_status)
            conn = queries.connect(self.db_path)
            cap = cv2.VideoCapture(str(self.video_path))
            if not cap.isOpened():
                raise RuntimeError(f"cannot open video {self.video_path}")
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            if not 1 <= fps <= 240:
                fps = 30.0
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0) or None
            self._set(state="running", video_fps=round(fps, 2), frames_in_clip=total, loop_number=1)

            self.pipeline.reset()
            loop, frame_in_clip, stream_offset, processed = 1, 0, 0.0, 0
            fps_ema, wall_start = None, time.monotonic()
            last_tick = wall_start
            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok:
                    if frame_in_clip == 0:
                        raise RuntimeError(f"no frames could be read from {self.video_path.name}")
                    # End of clip: start the next pass as a fresh session.
                    cap.release()
                    cap = cv2.VideoCapture(str(self.video_path))
                    stream_offset += frame_in_clip / fps + 1.0
                    loop, frame_in_clip = loop + 1, 0
                    self.pipeline.reset()
                    tracker.reset()
                    wall_start = time.monotonic()
                    self._set(loop_number=loop)
                    continue

                frame_in_clip += 1
                video_time = (frame_in_clip - 1) / fps
                t0 = time.monotonic()
                res = self.pipeline.process(frame, stream_offset + video_time, frame_in_clip)
                events = tracker.update(video_time, res["fall_now"], res["confidence"], res["posture"],
                                        res["labels"], res["objects"], gait=res["gait"])
                for event in events:
                    self._store(conn, event, video_time, frame_in_clip, loop)

                now = time.monotonic()
                if now > last_tick:
                    inst = 1.0 / (now - last_tick)
                    fps_ema = inst if fps_ema is None else 0.9 * fps_ema + 0.1 * inst
                last_tick = now
                self.pipeline.annotate(frame, res, tracker.alarm_active, fps_ema, tracker.hits, tracker.window)
                self._publish(cv2, frame)
                processed += 1
                people = [o for o in res["objects"] if o.get("class") == PERSON_CLASS]
                self._set(frames_processed=processed, processing_fps=round(fps_ema, 2) if fps_ema else None,
                          frame_in_clip=frame_in_clip, video_time=round(video_time, 2),
                          posture=res["posture"], fall_signal=res["fall_now"],
                          alarm_active=tracker.alarm_active, fall_frames_in_window=tracker.hits,
                          people_in_view=len(people),
                          objects=[{"class": o["class"], "confidence": round(o["confidence"], 2)}
                                   for o in sorted(res["objects"], key=lambda o: -o["confidence"])[:8]],
                          gait=self.pipeline.gait_status,
                          last_frame_ms=round((now - t0) * 1000, 1))

                if self.pace_to_video:
                    # Never run ahead of the clip's own speed.
                    ahead = (frame_in_clip / fps) - (time.monotonic() - wall_start)
                    if ahead > 0:
                        self._stop.wait(ahead)
        except Exception as exc:  # report it on the status page instead of dying silently
            self._set(state="error", error=f"{type(exc).__name__}: {exc}")
            return
        finally:
            if cap is not None:
                cap.release()
            if conn is not None:
                conn.close()
            try:
                self.pipeline.close()
            except Exception:
                pass
            with self._frame_ready:
                self._frame_ready.notify_all()
        self._set(state="stopped")

    def _publish(self, cv2, frame):
        h, w = frame.shape[:2]
        if w > self.max_width:
            frame = cv2.resize(frame, (self.max_width, int(h * self.max_width / w)))
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
        if not ok:
            return
        with self._frame_ready:
            self._jpeg = buf.tobytes()  # memory only; replaced by the next frame
            self._frame_seq += 1
            self._frame_ready.notify_all()

    def _store(self, conn, event, video_time, frame_no, loop):
        queries.insert_pipeline_event(conn, {
            "type": event["type"], "confidence": event["confidence"], "source": self.video_path.name,
            "video_time": round(video_time, 2), "frame": frame_no, "loop_number": loop,
            "details_json": json.dumps(event["details"], sort_keys=True)})
        with self._lock:
            self._state["events_logged"] += 1
        if event["type"] == "fall_alert" and self.patient_external_id:
            # Confirmed alerts also go where the caregiver pages read them,
            # through the same data-source layer the live API uses.
            record = {"event_id": f"live-{self._state['started_at']}-{loop}-{frame_no}",
                      "patient": self.patient_external_id, "timestamp": _now_iso(), "type": "fall",
                      "confidence": max(0.0, min(1.0, event["confidence"] or 0.0)),
                      "source": f"live:{self.video_path.name}",
                      "details": {**event["details"], "video_time": round(video_time, 2),
                                  "frame": frame_no, "loop": loop}}
            ingest(conn, PipelineSource(json.dumps(record).encode("utf-8")))
        live.notify()


# --- one service per server process ---------------------------------------------------------

_service = None
_service_lock = threading.Lock()


def start_service(**kwargs):
    """Start the single processing service, or return the one already running."""
    global _service
    with _service_lock:
        if _service is None or not _service.is_running:
            _service = VideoProcessingService(**kwargs)
            _service.start()
        return _service


def get_service():
    return _service


def stop_service():
    global _service
    with _service_lock:
        if _service is not None:
            _service.stop()
        _service = None
