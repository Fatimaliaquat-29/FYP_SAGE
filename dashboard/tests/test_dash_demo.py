"""Live demo: background video processing, event logging, the demo page and its endpoints.

Most tests use a FakePipeline with the same interface as SagePipeline, so they
run in seconds. `test_real_pipeline_end_to_end` (marked `models`) runs the real
S.A.G.E. models on a real clip.
"""

import ast
import json
import random
import re
import threading
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np
import pytest

from conftest import CSRF, DASHBOARD_DIR, make_app, sign_in
from sage_dashboard import demo_service, queries
from sage_dashboard.demo_service import EventTracker, VideoProcessingService

REPO_ROOT = DASHBOARD_DIR.parent


# --- helpers ----------------------------------------------------------------------

def make_video(path, frames=20, fps=20, size=(64, 48)):
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), fps, size)
    for i in range(frames):
        img = np.full((size[1], size[0], 3), (i * 10) % 255, dtype=np.uint8)
        writer.write(img)
    writer.release()
    return path


def gait_result(score):
    """A GaitRiskAssessor.assess_risk() result, in its documented shape."""
    return {"risk_score": score, "signals": [
        {"name": "walking_speed", "available": score is not None, "value": 0.5,
         "risk_contribution": score},
        {"name": "stride_regularity", "available": False, "value": None, "risk_contribution": None},
        {"name": "postural_sway", "available": False, "value": None, "risk_contribution": None},
        {"name": "sit_to_stand", "available": False, "value": None, "risk_contribution": None}]}


class FakePipeline:
    """Scripted per-frame results with SagePipeline's interface (no models)."""

    def __init__(self, person_frames=range(3, 16), fall_frames=range(8, 15), delay=0.0, fail_on_load=False,
                 gait_scores=None):
        self.person_frames, self.fall_frames = set(person_frames), set(fall_frames)
        self.delay, self.fail_on_load = delay, fail_on_load
        # frame number -> risk score of a fresh gait result on that frame
        self.gait_scores = {5: 0.2, 10: 0.3, 15: 0.55} if gait_scores is None else gait_scores
        self.loads = self.resets = self.closes = 0
        self.processed = []
        self.last_gait = None

    def load(self):
        self.loads += 1
        if self.fail_on_load:
            raise RuntimeError("model file missing")

    alert_settings = {"window": 12, "min_hits": 4, "hold": 5.0}
    components = {"pose": True, "heuristic": True, "lstm": False, "object_detection": True,
                  "object_model": "fake.pt", "gait": True}

    @property
    def gait_status(self):
        score = self.last_gait
        return {"running": True, "error": None, "window_frames": 150, "frames_buffered": min(self.frame_no, 150),
                "reassess_every": 15, "baseline_mode": "3d" if score is not None else None,
                "assessments": self.assessments, "risk_score": score,
                "band": None if score is None else ("medium" if score >= 0.4 else "low"), "signals": {}}

    frame_no = assessments = 0

    def reset(self):
        self.resets += 1
        self.last_gait = None
        self.frame_no = self.assessments = 0

    def process(self, frame, stream_seconds, frame_no):
        self.processed.append((frame_no, stream_seconds))
        if self.delay:
            time.sleep(self.delay)
        objects = [{"class": "chair", "confidence": 0.9, "bbox": [0, 0, 5, 5]}]
        if frame_no in self.person_frames:
            objects.append({"class": "person", "confidence": 0.8, "bbox": [1, 1, 9, 9]})
        fall = frame_no in self.fall_frames
        gait = None
        self.frame_no = frame_no
        if frame_no in self.gait_scores:
            self.last_gait = self.gait_scores[frame_no]
            self.assessments += 1
            gait = gait_result(self.last_gait)
        return {"posture": "Lying" if fall else "Standing", "fall_now": fall, "confidence": 0.9 if fall else 0.5,
                "labels": "horizontal_torso" if fall else "", "landmarks": [], "visibility": [], "objects": objects,
                "gait": gait}

    def annotate(self, frame, res, alarm_active, fps, hits, window):
        pass

    def close(self):
        self.closes += 1


def wait_until(condition, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if condition():
            return True
        time.sleep(0.05)
    return False


@pytest.fixture
def video(tmp_path):
    return make_video(tmp_path / "clip.avi")


@pytest.fixture
def with_patient(db_path):
    conn = queries.connect(db_path)
    queries.upsert_patient(conn, "P001", "Amina Rahman")
    conn.commit()
    conn.close()


@pytest.fixture
def service(video, db_path, with_patient):
    started = []

    def start(pipeline=None, **kwargs):
        svc = VideoProcessingService(video_path=video, db_path=db_path, pipeline=pipeline or FakePipeline(),
                                     patient_external_id="P001", pace_to_video=False, **kwargs)
        svc.start()
        started.append(svc)
        return svc
    yield start
    for svc in started:
        svc.stop()


@pytest.fixture(autouse=True)
def no_leftover_service():
    yield
    demo_service.stop_service()


# --- the alert rule matches realtime_fall_detection.py --------------------------------

def realtime_constants():
    tree = ast.parse((REPO_ROOT / "realtime_fall_detection.py").read_text(encoding="utf-8"))
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ("ALERT_WINDOW", "ALERT_MIN_HITS", "ALERT_HOLD_SECONDS", "HISTORY_CAP"):
                values[name] = ast.literal_eval(node.value)
    return values


def test_fallback_constants_match_realtime_script():
    c = realtime_constants()
    assert (c["ALERT_WINDOW"], c["ALERT_MIN_HITS"], c["ALERT_HOLD_SECONDS"], c["HISTORY_CAP"]) == \
        (demo_service.ALERT_WINDOW, demo_service.ALERT_MIN_HITS, demo_service.ALERT_HOLD_SECONDS,
         demo_service.HISTORY_CAP)


def reference_alerts(flags, times, window, min_hits, hold):
    """The debounce exactly as written in realtime_fall_detection.run()."""
    fall_flags, alarm_active, alarm_until, alerts = deque(maxlen=window), False, 0.0, []
    for i, (fall_now, now) in enumerate(zip(flags, times)):
        fall_flags.append(1 if fall_now else 0)
        hits = sum(fall_flags)
        if not alarm_active and hits >= min_hits:
            alarm_active, alarm_until = True, now + hold
            alerts.append(i)
        elif alarm_active and now >= alarm_until and hits == 0:
            alarm_active = False
    return alerts


@pytest.mark.parametrize("seed", range(20))
def test_fall_alerts_identical_to_realtime_debounce(seed):
    rng = random.Random(seed)
    flags, burst = [], 0
    for _ in range(1500):
        if burst:
            burst -= 1
        elif rng.random() < 0.02:
            burst = rng.randint(1, 60)
        flags.append(bool(burst) and rng.random() < 0.8)
    times = [i / 30 for i in range(len(flags))]
    tracker = EventTracker(12, 4, 5.0)
    got = [i for i, (f, t) in enumerate(zip(flags, times))
           if any(e["type"] == "fall_alert" for e in tracker.update(t, f))]
    expected = reference_alerts(flags, times, 12, 4, 5.0)
    assert len(expected) >= 2, "the random sequence should exercise several alerts"
    assert got == expected


def test_possible_fall_once_per_burst_and_not_during_alert():
    tr = EventTracker(window=4, min_hits=3, hold=1.0)
    types = lambda evs: [e["type"] for e in evs]  # noqa: E731
    assert types(tr.update(0.0, True, 0.7, "Lying", "x")) == ["possible_fall"]
    assert types(tr.update(0.1, True)) == []
    assert types(tr.update(0.2, True)) == ["fall_alert"]
    assert types(tr.update(0.3, True)) == []
    for i in range(4):
        tr.update(0.4 + i * 0.1, False)       # window clears, burst ends
    assert types(tr.update(1.5, True)) == []  # alarm still latched -> no "possible" while active
    for i in range(4):
        tr.update(1.6 + i * 0.1, False)
    assert types(tr.update(3.0, True)) == ["possible_fall"]  # re-armed: a new burst is reported


def test_short_signal_is_only_a_possible_fall():
    tr = EventTracker(window=12, min_hits=4, hold=5.0)
    events = [e for i in range(30) for e in tr.update(i / 30, i in (5, 6))]
    assert [e["type"] for e in events] == ["possible_fall"]
    assert events[0]["details"]["fall_frames_in_window"] == 1


def test_person_enter_and_leave_with_gap():
    tr = EventTracker(person_absent=2.0)
    person = [{"class": "person", "confidence": 0.8}]
    seen = []
    for i in range(200):
        t = i / 10
        present = 1 <= t < 5 or 5.5 <= t < 8   # a 0.5 s gap is a flicker, not leaving
        seen += [(round(t, 1), e["type"]) for e in tr.update(t, False, objects=person if present else [])]
    assert seen == [(1.0, "person_detected"), (9.9, "person_left")]


def test_reset_clears_everything():
    tr = EventTracker(window=4, min_hits=2)
    tr.update(0, True, objects=[{"class": "person", "confidence": 0.9}])
    tr.update(0.1, True)
    assert tr.alarm_active and tr.person_in_view
    tr.reset()
    assert not tr.alarm_active and not tr.person_in_view and tr.hits == 0


# --- gait ---------------------------------------------------------------------------

def test_gait_logged_on_first_score_and_band_changes_only():
    tr = EventTracker()
    logged = []
    for t, score in enumerate([None, 0.2, 0.3, 0.45, 0.5, 0.75, None, 0.72, 0.1]):
        logged += [(e["details"]["risk_score"], e["details"]["band"])
                   for e in tr.update(t, False, gait=gait_result(score)) if e["type"] == "gait_risk"]
    # 0.4 and 0.7 are the caregiver pages' medium/high cut-offs; a score that
    # could not be measured (None) is not logged and does not change the band
    assert logged == [(0.2, "low"), (0.45, "medium"), (0.75, "high"), (0.1, "low")]
    assert tr.update(10, False, gait=None) == []   # no fresh result this frame


def test_gait_event_records_which_signals_were_measured():
    event = EventTracker().update(0, False, gait=gait_result(0.62))[0]
    assert event == {"type": "gait_risk", "confidence": None,
                     "details": {"risk_score": 0.62, "band": "medium", "signals": {"walking_speed": 0.62}}}


def test_gait_band_starts_again_each_pass():
    tr = EventTracker()
    assert len(tr.update(0, False, gait=gait_result(0.3))) == 1
    tr.reset()
    assert tr.gait_score is None
    assert len(tr.update(0, False, gait=gait_result(0.3))) == 1


def test_fall_alert_carries_latest_gait_score_as_context():
    tr = EventTracker(window=4, min_hits=2)
    tr.update(0, False, gait=gait_result(0.66))
    tr.update(0.1, True)
    alert = next(e for e in tr.update(0.2, True) if e["type"] == "fall_alert")
    assert alert["details"]["gait_risk_score"] == 0.66


@pytest.mark.parametrize("seed", range(5))
def test_gait_never_changes_fall_alerts(seed):
    rng = random.Random(seed)
    flags = [rng.random() < 0.15 for _ in range(1500)]
    times = [i / 30 for i in range(len(flags))]
    tracker = EventTracker(12, 4, 5.0)
    got = []
    for i, (f, t) in enumerate(zip(flags, times)):
        gait = gait_result(rng.choice([None, 0.1, 0.5, 0.9])) if i % 15 == 0 else None
        if any(e["type"] == "fall_alert" for e in tracker.update(t, f, gait=gait)):
            got.append(i)
    assert got == reference_alerts(flags, times, 12, 4, 5.0)


def test_gait_row_adds_3d_landmarks_on_a_copy():
    nan = float("nan")
    keypoints = [0.5, 0.5] * 33
    keypoints[2:4] = [nan, nan]   # joint 1 was dropped as not visible
    row = {"frame": 3, "keypoints": keypoints, "posture_label": "Standing"}
    world = [(0.1 * i, 0.2, 0.3) for i in range(33)]
    out = demo_service.gait_row(row, world, 33)
    assert "world_keypoints" not in row, "the row fall detection saw is not changed"
    assert out["posture_label"] == "Standing" and out["keypoints"] is keypoints
    wk = out["world_keypoints"]
    assert len(wk) == 99 and wk[0:3] == [0.0, 0.2, 0.3] and wk[6:9] == pytest.approx([0.2, 0.2, 0.3])
    assert all(v != v for v in wk[3:6]), "a joint not trusted in 2D is not trusted in 3D either"
    assert "world_keypoints" not in demo_service.gait_row(row, [], 33)
    assert len(demo_service.gait_row(row, world[:10], 33)["world_keypoints"]) == 99


def test_real_gait_classes_with_the_realtime_settings():
    import inspect
    import sys
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from src.gait import gait_stream
    pipe = demo_service.SagePipeline()
    pipe.gait_stream = gait_stream
    pipe.gait_window = inspect.signature(
        gait_stream.StreamingGaitRiskAssessor.__init__).parameters["window_frames"].default
    pipe._new_gait_session()
    assert isinstance(pipe.gait, gait_stream.StreamingGaitRiskAssessor)
    assert isinstance(pipe.calibrator, gait_stream.TorsoBaselineCalibrator)
    st = pipe.gait_status
    assert st["running"] and st["window_frames"] == 150 and st["reassess_every"] == 15
    assert st["assessments"] == 0 and st["risk_score"] is None and st["baseline_mode"] is None
    json.dumps(st)


class FakeGaitStream:
    """Stands in for src.gait.gait_stream, counting what the pipeline does with it."""

    def __init__(self, scores, fail_at=()):
        self.scores, self.fail_at, self.made = list(scores), set(fail_at), 0
        self.rows = []
        stream = self

        class Assessor:
            def __init__(self, window_frames, reassess_every_n_frames):
                stream.made += 1
                self.baseline = None

            def set_torso_baseline(self, value):
                self.baseline = value

            def push_frame(self, row):
                stream.rows.append(row)
                if row["frame"] in stream.fail_at:
                    raise ValueError("bad window")
                score = stream.scores.pop(0) if stream.scores else "none"
                return None if score == "none" else gait_result(score)

        class Calibrator:
            def __init__(self, min_run_frames):
                self.baseline = self.baseline_mode = None

            @property
            def is_calibrated(self):
                return self.baseline is not None

            def observe(self, row, posture, fall):
                if posture == "Standing" and not fall:
                    self.baseline, self.baseline_mode = 0.3, "3d"
                    return True
                return False

        self.StreamingGaitRiskAssessor, self.TorsoBaselineCalibrator = Assessor, Calibrator


def gait_pipeline(stream):
    pipe = demo_service.SagePipeline()
    pipe.gait_stream, pipe.gait_window = stream, 150
    pipe._new_gait_session()
    return pipe


def test_gait_error_is_reported_and_never_raised():
    stream = FakeGaitStream(["none", 0.4], fail_at={2})
    pipe = gait_pipeline(stream)
    assert pipe._push_gait({"frame": 1}, "Standing", False, 1) is None
    assert pipe.gait.baseline == 0.3, "calibration hands the baseline to the assessor"
    assert pipe._push_gait({"frame": 2}, "Lying", True, 2) is None   # raises inside gait
    assert "frame 2: ValueError: bad window" in pipe.gait_status["error"]
    assert pipe._push_gait({"frame": 3}, "Lying", True, 3)["risk_score"] == 0.4
    st = pipe.gait_status
    assert st["assessments"] == 1 and st["risk_score"] == 0.4 and st["band"] == "medium"
    assert st["baseline_mode"] == "3d" and st["signals"] == {"walking_speed": 0.4}


def test_each_pass_gets_a_fresh_gait_session():
    class FakeUtils:
        resets = 0

        def reset_session_state(self):
            FakeUtils.resets += 1

    stream = FakeGaitStream([0.5])
    pipe = gait_pipeline(stream)
    pipe.pu = FakeUtils()
    pipe._push_gait({"frame": 1}, "Standing", False, 1)
    assert pipe.gait_status["assessments"] == 1
    pipe.reset()
    assert stream.made == 2 and FakeUtils.resets == 1
    st = pipe.gait_status
    assert st["assessments"] == 0 and st["risk_score"] is None and st["baseline_mode"] is None


@pytest.mark.parametrize("status", [
    {"running": True, "assessments": 0, "baseline_mode": None, "risk_score": None},
    {"running": True, "assessments": 2, "baseline_mode": "3d", "risk_score": None},
    {"running": True, "assessments": 2, "baseline_mode": "2d", "risk_score": 0.71},
], ids=["warming-up", "not-measurable", "score"])
def test_gait_overlay_line_is_drawn(status):
    frame = np.zeros((240, 320, 3), dtype=np.uint8)
    demo_service._draw_gait(frame, status)
    assert frame[125:150].any() and not frame[:120].any(), "one line of text, below the fall overlay"
    blank = np.zeros_like(frame)
    demo_service._draw_gait(blank, {"running": False, "error": None})
    assert not blank.any()


def test_gait_turned_off():
    pipe = demo_service.SagePipeline(use_gait=False)
    assert pipe.gait_status == {"running": False, "error": None}
    assert pipe._push_gait({"frame": 1}, "Standing", False, 1) is None


# --- the background service -------------------------------------------------------------

def test_service_loops_logs_events_and_publishes_frames(service, db_path):
    pipe = FakePipeline()
    svc = service(pipe)
    assert wait_until(lambda: svc.status()["loop_number"] >= 3)
    st = svc.status()
    assert st["state"] == "running" and st["video"] == "clip.avi"
    assert st["frames_processed"] >= 40 and st["video_fps"] == 20
    assert st["components"]["object_detection"] is True and st["alert_window"] == 12
    assert pipe.loads == 1, "models are loaded once, not per pass or per viewer"
    assert pipe.resets >= 3, "each pass through the clip starts a fresh session"
    seq, jpeg = svc.wait_for_frame(0, timeout=2)
    assert seq > 0 and jpeg[:2] == b"\xff\xd8"
    svc.stop()
    assert svc.status()["state"] == "stopped" and pipe.closes == 1

    conn = queries.connect(db_path)
    counts = queries.pipeline_event_counts(conn)
    rows = queries.pipeline_events_after(conn, 0, 200)
    caregiver = queries.query_events(conn, 1, limit=50)
    conn.close()
    loops = max(r["loop_number"] for r in rows)
    assert counts["person_detected"] >= loops - 1 and counts["fall_alert"] >= loops - 1
    # Every complete pass: one possible fall (frame 8), then one alert (frame 11).
    # The last pass may have been stopped part-way, so it is left out.
    for loop in range(1, loops):
        in_pass = sorted((r["frame"], r["type"]) for r in rows
                         if r["loop_number"] == loop and r["type"] in ("possible_fall", "fall_alert"))
        assert in_pass == [(8, "possible_fall"), (11, "fall_alert")], (loop, in_pass)
    alert = next(r for r in rows if r["type"] == "fall_alert")
    assert alert["frame"] == 11 and alert["source"] == "clip.avi"   # 4th flagged frame (8..11)
    assert json.loads(alert["details_json"])["posture"] == "Lying"
    assert len(caregiver) == counts["fall_alert"]
    assert all(e["type"] == "fall" and e["source"] == "live:clip.avi" for e in caregiver)


def test_service_logs_gait_and_shows_it_in_status(service, db_path):
    svc = service(FakePipeline(gait_scores={5: 0.2, 10: 0.3, 15: 0.55}))
    assert wait_until(lambda: svc.status()["loop_number"] >= 3)
    st = svc.status()
    assert st["components"]["gait"] is True and st["gait"]["running"] is True
    svc.stop()
    conn = queries.connect(db_path)
    logged = queries.pipeline_events_after(conn, 0, 200)
    caregiver = queries.query_events(conn, 1, limit=50)
    conn.close()
    rows = [r for r in logged if r["type"] == "gait_risk"]
    first_pass = sorted((r["frame"], json.loads(r["details_json"])["band"]) for r in rows if r["loop_number"] == 1)
    assert first_pass == [(5, "low"), (15, "medium")]       # 0.3 stays "low", so it is not logged
    assert {r["loop_number"] for r in rows} >= {1, 2}       # each pass starts its own record
    assert all(r["confidence"] is None for r in rows)
    assert all(e["type"] == "fall" for e in caregiver), "gait scores stay in the demo log"
    alert = next(r for r in logged if r["type"] == "fall_alert")
    assert json.loads(alert["details_json"])["gait_risk_score"] == 0.3   # latest score at frame 11


def test_stream_time_keeps_rising_across_passes(service):
    pipe = FakePipeline()
    svc = service(pipe)
    assert wait_until(lambda: svc.status()["loop_number"] >= 2 and svc.status()["frame_in_clip"] > 3)
    times = [t for _, t in pipe.processed]
    assert all(b > a for a, b in zip(times, times[1:])), "pose tracking needs ever-increasing timestamps"


def test_no_frames_written_to_disk(service, tmp_path, video):
    svc = service()
    assert wait_until(lambda: svc.status()["frames_processed"] > 30)
    svc.stop()
    files = {p.name for p in tmp_path.rglob("*") if p.is_file()}
    assert not any(name.endswith((".jpg", ".jpeg", ".png", ".mp4")) for name in files)


def test_paced_to_clip_speed(video, db_path, with_patient):
    svc = VideoProcessingService(video_path=video, db_path=db_path, pipeline=FakePipeline(), pace_to_video=True)
    svc.start()
    try:
        time.sleep(1.5)
        processed = svc.status()["frames_processed"]
    finally:
        svc.stop()
    assert 15 <= processed <= 40  # 20 fps clip: never runs ahead of real time


def test_bad_video_reports_error(tmp_path, db_path):
    svc = VideoProcessingService(video_path=tmp_path / "missing.mp4", db_path=db_path, pipeline=FakePipeline())
    svc.start()
    assert wait_until(lambda: svc.status()["state"] == "error")
    assert "cannot open video" in svc.status()["error"]


def test_model_load_failure_reported(video, db_path):
    svc = VideoProcessingService(video_path=video, db_path=db_path, pipeline=FakePipeline(fail_on_load=True))
    svc.start()
    assert wait_until(lambda: svc.status()["state"] == "error")
    assert "model file missing" in svc.status()["error"]


def test_only_one_service_per_server(video, db_path, with_patient):
    a = demo_service.start_service(video_path=video, db_path=db_path, pipeline=FakePipeline(delay=0.01),
                                   pace_to_video=False)
    b = demo_service.start_service(video_path=video, db_path=db_path, pipeline=FakePipeline(),
                                   pace_to_video=False)
    assert a is b and demo_service.get_service() is a
    workers = [t for t in threading.enumerate() if t.name == "sage-video-processing"]
    assert len(workers) == 1


# --- pages and endpoints -------------------------------------------------------------------

@pytest.fixture
def demo_app(db_path, user_ids, with_patient):
    return make_app(db_path)


@pytest.fixture
def demo_client(demo_app, user_ids):
    return sign_in(demo_app.test_client(), user_ids["admin"])


def test_demo_page_needs_sign_in(demo_app):
    assert demo_app.test_client().get("/demo").status_code == 302
    for url in ("/live/demo/status", "/live/demo/events", "/live/demo/video.mjpg"):
        assert demo_app.test_client().get(url).status_code == 401


def test_demo_page_renders_three_tabs(demo_client):
    body = demo_client.get("/demo").get_data(as_text=True)
    for tab in ("Live monitoring", "Event log", "System status"):
        assert f">{tab}" in body
    assert 'role="tablist"' in body and 'src="/static/demo.js"' in body


def test_status_without_service(demo_client):
    data = demo_client.get("/live/demo/status").get_json()
    assert data["state"] == "not_started" and data["total_events"] == 0 and data["latest_event"] is None
    assert demo_client.get("/live/demo/video.mjpg").status_code == 503


def test_status_events_and_video_with_service(demo_client, video, db_path):
    svc = demo_service.start_service(video_path=video, db_path=db_path, pipeline=FakePipeline(),
                                     patient_external_id="P001", pace_to_video=False)
    assert wait_until(lambda: svc.status()["loop_number"] >= 2)
    data = demo_client.get("/live/demo/status").get_json()
    assert data["state"] == "running" and data["total_events"] > 0
    assert data["counts"]["fall_alert"] >= 1 and data["latest_event"]["label"]
    events = demo_client.get("/live/demo/events").get_json()["events"]
    assert events and events == sorted(events, key=lambda e: -e["id"])
    newest = events[0]["id"]
    assert all(e["id"] > newest for e in demo_client.get(f"/live/demo/events?after={newest}").get_json()["events"])
    assert demo_client.get("/live/demo/events?after=abc").status_code == 400

    resp = demo_client.get("/live/demo/video.mjpg", buffered=False)
    assert resp.mimetype == "multipart/x-mixed-replace"
    chunk = next(iter(resp.response))
    assert chunk.startswith(b"--frame\r\nContent-Type: image/jpeg") and b"\xff\xd8" in chunk
    before = svc.status()["frames_processed"]
    resp.close()  # a viewer going away...
    assert wait_until(lambda: svc.status()["frames_processed"] > before + 10)  # ...does not stop processing
    assert svc.is_running


def test_polling_does_not_keep_session_alive(demo_client):
    old = time.time() - 30 * 60
    with demo_client.session_transaction() as s:
        s["last_seen"] = old
    demo_client.get("/live/demo/status", headers={"X-Live-Refresh": "1"})
    demo_client.get("/live/demo/events")
    with demo_client.session_transaction() as s:
        assert s["last_seen"] == old


def test_demo_command_rejects_missing_video(db_path, capsys):
    import manage
    assert manage.main(["--db", str(db_path), "demo", "--video", "nope.mp4"]) == 2
    assert "Video not found" in capsys.readouterr().err


# --- the real models (slow) ------------------------------------------------------------------

REAL_CLIP = REPO_ROOT / "test_footage" / "Hussain Testing 7-30-26" / "Moving_in_out_frame_withFall.MOV"


@pytest.mark.models
@pytest.mark.skipif(not REAL_CLIP.is_file(), reason="test footage not present")
def test_real_pipeline_end_to_end(db_path, with_patient):
    pipeline = demo_service.SagePipeline()
    svc = VideoProcessingService(video_path=REAL_CLIP, db_path=db_path, pipeline=pipeline,
                                 patient_external_id="P001", pace_to_video=False)
    svc.start()
    try:
        assert wait_until(lambda: svc.status()["state"] in ("running", "error"), timeout=400)
        assert wait_until(lambda: svc.status()["frames_processed"] >= 200 or svc.status()["state"] == "error",
                          timeout=300)
        st = svc.status()
        assert st["state"] == "running", st["error"]
        assert st["components"]["pose"] and st["components"]["heuristic"] and st["components"]["object_detection"]
        assert st["components"]["gait"] and st["gait"]["error"] is None
        # 150-frame window, a fresh assessment every 15 frames after that. On
        # this clip they come back unscored (risk_score None): see the README.
        assert st["gait"]["assessments"] >= 3 and st["gait"]["window_frames"] == 150
        conn = queries.connect(db_path)
        counts = queries.pipeline_event_counts(conn)
        conn.close()
        assert counts.get("person_detected", 0) >= 1
        assert counts.get("fall_alert", 0) >= 1, counts   # this clip contains a fall
    finally:
        svc.stop()


# --- in a real browser -------------------------------------------------------------------

@pytest.fixture
def demo_server(tmp_path, db_path, user_ids, with_patient):
    pytest.importorskip("playwright")
    from werkzeug.serving import make_server
    clip = make_video(tmp_path / "long.avi", frames=120, fps=20, size=(320, 180))   # 6 s per pass
    svc = demo_service.start_service(video_path=clip, db_path=db_path,
                                     pipeline=FakePipeline(person_frames=range(10, 100), fall_frames=range(40, 80)),
                                     patient_external_id="P001", pace_to_video=True)
    server = make_server("127.0.0.1", 0, make_app(db_path, TESTING=False), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}", svc
    server.shutdown()


@pytest.fixture
def browser_page():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        contexts = []

        def make(width):
            ctx = browser.new_context(viewport={"width": width, "height": 900})
            contexts.append(ctx)
            return ctx.new_page()
        yield make
        for ctx in contexts:
            ctx.close()
        browser.close()


def test_tab_switching_never_interrupts_processing(demo_server, browser_page):
    from playwright.sync_api import expect
    from test_dash_ui import sign_in as ui_sign_in
    url, svc = demo_server
    page = browser_page(1440)
    ui_sign_in(page, url)
    page.goto(url + "/demo")
    expect(page.locator("#demo-state")).to_contain_text("Running")
    page.wait_for_function("document.getElementById('demo-video').naturalWidth > 0", timeout=10000)
    page.evaluate("window.__noReload = true")
    start = svc.status()

    page.get_by_role("tab", name="Event log").click()
    expect(page.locator("#panel-live")).to_be_hidden()
    assert page.get_attribute("#demo-video", "src") is None   # this viewer stops receiving frames...
    rows = page.locator("#demo-log-body tr")
    first_count = rows.count()
    expect(rows.first).to_be_visible(timeout=15000)
    page.wait_for_timeout(7000)                                 # ...more than one pass of the clip
    middle = svc.status()
    assert middle["frames_processed"] > start["frames_processed"] + 60   # ...but processing carried on
    assert rows.count() > first_count                            # and new events arrived without a refresh
    expect(page.locator("#demo-log-body")).to_contain_text("Fall alert")
    expect(page.locator("#demo-log-body")).to_contain_text("Walking (gait) risk")
    expect(page.locator("#demo-log-body")).to_contain_text("risk 0.55 (medium)")

    page.get_by_role("tab", name="System status").click()
    expect(page.locator("#panel-status")).to_contain_text("Running (fake.pt)")
    expect(page.locator('#panel-status [data-field="gait_component_label"]')).to_have_text("Running")
    expect(page.locator('#panel-status [data-field="gait_window_label"]')).to_contain_text(
        re.compile(r"^\d+ of 150, new score every 15 frames$"))
    expect(page.locator('#panel-status [data-field="count_gait_risk"]')).not_to_have_text("0")
    page.get_by_role("tab", name="Live monitoring").click()
    expect(page.locator('#panel-live [data-field="gait_label"]')).to_have_text(
        re.compile(r"^(\d\.\d\d \((low|medium)\)|Warming up \(\d+ of 150 frames\))$"))
    page.wait_for_function("document.getElementById('demo-video').naturalWidth > 0", timeout=10000)
    end = svc.status()
    assert end["frames_processed"] > middle["frames_processed"]
    assert (end["loop_number"], end["frame_in_clip"]) > (start["loop_number"], start["frame_in_clip"]), \
        "coming back shows the current position, not the start of the video"
    assert page.evaluate("window.__noReload") is True
    assert svc.pipeline.loads == 1


@pytest.mark.parametrize("width", [360, 768, 1440])
@pytest.mark.parametrize("tab", ["live", "events", "status"])
def test_demo_layout(demo_server, browser_page, width, tab):
    from playwright.sync_api import expect
    from test_dash_ui import (CONTRAST_JS, OVERFLOW_JS, SMALL_TARGETS_JS, TEXT_SIZE_JS,
                              sign_in as ui_sign_in)
    url, svc = demo_server
    page = browser_page(width)
    ui_sign_in(page, url)
    page.goto(f"{url}/demo#{tab}")
    expect(page.locator("#demo-state")).to_contain_text("Running")
    expect(page.locator("#demo-log-body tr").first).to_be_attached(timeout=15000)
    page.wait_for_timeout(500)
    assert page.evaluate(OVERFLOW_JS) == []
    assert page.evaluate(SMALL_TARGETS_JS) == []
    assert page.evaluate(TEXT_SIZE_JS) == []
    assert page.evaluate(CONTRAST_JS) == []


def test_tabs_work_with_keyboard(demo_server, browser_page):
    from playwright.sync_api import expect
    from test_dash_ui import sign_in as ui_sign_in
    url, _ = demo_server
    page = browser_page(768)
    ui_sign_in(page, url)
    page.goto(url + "/demo")
    page.get_by_role("tab", name="Live monitoring").focus()
    page.keyboard.press("ArrowRight")
    expect(page.get_by_role("tab", name="Event log")).to_be_focused()
    expect(page.get_by_role("tab", name="Event log")).to_have_attribute("aria-selected", "true")
    expect(page.locator("#panel-events")).to_be_visible()
