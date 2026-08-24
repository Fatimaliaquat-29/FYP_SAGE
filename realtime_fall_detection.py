"""
realtime_fall_detection.py
==========================
Live (real-time) fall detection for the S.A.G.E. pipeline.

Runs the SAME hybrid logic used offline -- the rule-based heuristic
(pipeline_utils.classify_posture_and_fall) OR the temporal LSTM -- on a live
camera (or any video file), frame by frame, and raises a DEBOUNCED fall alert.

Why a debounce (and why it matters for elderly monitoring)
----------------------------------------------------------
A single-frame fall trigger can come from a landmark glitch or a momentary
ambiguous posture. Alerting on one frame causes false alarms; too many false
alarms cause alarm fatigue and the caregiver starts ignoring the system --
which is just as dangerous as missing a fall. So an ALERT is only raised when
the fall signal is present in at least ALERT_MIN_HITS of the last ALERT_WINDOW
frames, and then it latches for ALERT_HOLD_SECONDS before it can re-arm. This
turns the frame-level (recall-biased) detector into a stable, low-false-alarm
event signal without sacrificing real falls (a genuine fall keeps firing for
many consecutive frames as the person stays on the floor).

Usage
-----
  # Live webcam (device 0):
  python realtime_fall_detection.py

  # A specific camera or a video file (great for replaying a test clip live):
  python realtime_fall_detection.py --input 1
  python realtime_fall_detection.py --input test_footage/Normal_Fall_1.mov

  # Heuristic only (skip the LSTM), headless (no window), or hide the skeleton:
  python realtime_fall_detection.py --no-lstm --no-display --no-skeleton

Press 'q' to quit.
"""

import argparse
import inspect
import sys
import time
from collections import deque
from pathlib import Path

import cv2
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import mediapipe as mp

from src.posture.pipeline_utils import (
    LANDMARK_COUNT,
    MIN_LANDMARK_VISIBILITY,
    build_pose_row,
    classify_posture_and_fall,
    reset_session_state,
)
from src.detection.yolo_objects import YOLOObjectDetector
from src.gait.gait_stream import StreamingGaitRiskAssessor, TorsoBaselineCalibrator

POSE_MODEL_PATH = str(REPO_ROOT / "models" / "pose_landmarker_full.task")
DEFAULT_OBJECT_MODEL_PATH = REPO_ROOT / "models" / "yolov8n_sage_merged_v3.pt"

# ── Alert debounce defaults ────────────────────────────────────────────────
ALERT_WINDOW      = 12    # look at the last N frames
ALERT_MIN_HITS    = 4     # need this many fall-flagged frames within the window
ALERT_HOLD_SECONDS = 5.0  # keep the alarm latched this long before it can re-arm

# Cap on retained history. The heuristic's dynamic calibration scans up to the
# last ~300 Standing frames, and the LSTM needs window_size+1; 320 covers both
# while keeping a long-running session's memory bounded.
HISTORY_CAP = 320

# ── GAIT streaming defaults ────────────────────────────────────────────────
# GAIT is a separate, PARALLEL signal, not part of the fall_detected decision
# path (see docs/IMPLEMENTATION_PLAN.md Section 5.3: "Gait's risk score is a
# separate, parallel output ... wired into a dashboard/alert system as its
# own independent signal" -- this is that wiring). See src/gait/gait_risk.py's
# own module docstring for why: it is a risk-score interface, not a
# fall/no-fall classifier, and stays that way here too -- nothing below ever
# feeds `fall_flags`/`alarm_active`.
#
# gait_features.MIN_WINDOW_FRAMES (90) is the hard floor `RingFrameBuffer`
# enforces; gait_stream.StreamingGaitRiskAssessor's own constructor default
# (~5s at 30fps) is the intended live-streaming value per that module's
# docstring -- reused here rather than re-derived, since nothing about this
# integration changes what window length is appropriate. Read directly off
# the class's own signature (a later audit session's config-drift fix)
# instead of a second hardcoded literal, so a future retune of that default
# can't silently desync this caller.
GAIT_WINDOW_FRAMES = inspect.signature(StreamingGaitRiskAssessor.__init__).parameters["window_frames"].default
GAIT_REASSESS_EVERY_N_FRAMES = 15
# Minimum contiguous CONFIRMED-Standing, non-fall frames (see
# gait_stream.TorsoBaselineCalibrator's own docstring for the full safety
# rationale) before a torso-length calibration is even attempted. ~2s at
# 30fps -- generous headroom over gait_features.CALIBRATION_SEGMENT_FRAMES
# (20) so that function's own least-noisy-sub-segment search has real room
# to work with, matching the calibrator's own documented default.
GAIT_MIN_CALIBRATION_FRAMES = 60

# Standard 33-point MediaPipe Pose topology (index meanings per the official
# spec: 0 nose, 11/12 shoulders, 23/24 hips, 25/26 knees, 27/28 ankles, ...).
# Hardcoded here because this installed MediaPipe build only exposes the
# Tasks API (mp.tasks.vision.PoseLandmarker) -- the legacy mp.solutions.pose
# module that normally provides POSE_CONNECTIONS is not available.
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24),
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),
]


def _make_detector():
    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=POSE_MODEL_PATH),
        # VIDEO (not IMAGE) mode: MediaPipe then tracks landmarks across frames
        # instead of re-detecting each frame from scratch. IMAGE mode treats a
        # live feed as unrelated stills, so landmarks jitter frame-to-frame --
        # and that jitter is what the fall logic reads as sudden hip velocity
        # and torso rotation, i.e. false alarms out of a stationary person.
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
    )
    return PoseLandmarker.create_from_options(options)


def _load_lstm(enabled: bool):
    if not enabled:
        return None
    try:
        from src.posture.lstm.lstm_classifier import LSTMPostureClassifier
        clf = LSTMPostureClassifier()
        if clf.is_available:
            print("[realtime] LSTM classifier loaded — running HYBRID (heuristic OR LSTM).")
            return clf
        print("[realtime] LSTM unavailable — running heuristic only.")
    except Exception as e:
        print(f"[realtime] Could not load LSTM ({e}) — running heuristic only.")
    return None


def _load_gait(enabled: bool, window_frames: int = GAIT_WINDOW_FRAMES,
               reassess_every_n_frames: int = GAIT_REASSESS_EVERY_N_FRAMES,
               min_calibration_frames: int = GAIT_MIN_CALIBRATION_FRAMES):
    """Mirrors `_load_lstm`/`_load_object_detector`'s own defensive-loading
    pattern: GAIT is an ADDITIVE, non-gating signal (see GAIT_WINDOW_FRAMES's
    own comment), so a failure constructing it must never prevent fall
    detection itself from starting. Returns (assessor, calibrator), both
    None if disabled or construction failed."""
    if not enabled:
        return None, None
    try:
        assessor = StreamingGaitRiskAssessor(
            window_frames=window_frames, reassess_every_n_frames=reassess_every_n_frames)
        calibrator = TorsoBaselineCalibrator(min_run_frames=min_calibration_frames)
        print(f"[realtime] GAIT streaming assessor loaded (window={window_frames} frames, "
              f"reassess every {reassess_every_n_frames} frames).")
        return assessor, calibrator
    except Exception as e:
        print(f"[realtime] Could not load GAIT assessor ({e}) — running without gait risk.")
        return None, None


def _load_object_detector(enabled: bool, model_path: Path, conf: float, imgsz: int):
    # Independent of the pose/fall pipeline -- object detection never gates or
    # feeds the fall alarm (that stays purely posture/LSTM-driven). It only
    # adds furniture/person-box context on screen. If it fails to load, fall
    # detection must keep working, so this never raises.
    if not enabled:
        return None
    try:
        detector = YOLOObjectDetector(model_path=model_path, confidence_threshold=conf, imgsz=imgsz)
        print(f"[realtime] Object detector loaded ({model_path.name}, conf={conf}, imgsz={imgsz}).")
        return detector
    except Exception as e:
        print(f"[realtime] Could not load object detector ({e}) — running pose-only.")
        return None


def run(input_source, use_lstm=True, show_display=True, show_skeleton=True,
        alert_window=ALERT_WINDOW, alert_min_hits=ALERT_MIN_HITS,
        alert_hold=ALERT_HOLD_SECONDS, on_alert=None,
        min_visibility=MIN_LANDMARK_VISIBILITY,
        use_objects=True, object_model_path=DEFAULT_OBJECT_MODEL_PATH,
        object_conf=0.25, object_imgsz=320,
        use_gait=True, on_gait_update=None,
        gait_window_frames=GAIT_WINDOW_FRAMES,
        gait_reassess_every_n_frames=GAIT_REASSESS_EVERY_N_FRAMES,
        gait_min_calibration_frames=GAIT_MIN_CALIBRATION_FRAMES):
    """
    Main real-time loop.

    Parameters
    ----------
    input_source : int | str
        Camera index (int) or path to a video file.
    on_alert : callable(dict) | None
        Optional callback invoked once per confirmed fall event. Receives a
        dict with keys: frame, timestamp, posture, source ("heuristic"/"lstm"/
        "hybrid"). Hook your SMS/email/dashboard notification here.
    use_gait : bool
        Run the GAIT (gait-quality fall-RISK) streaming assessor alongside
        fall detection -- see "GAIT integration" below. Defaults on; a
        failure to load it never blocks fall detection itself (see
        `_load_gait`).
    on_gait_update : callable(dict) | None
        Optional callback invoked every time the GAIT streaming assessor
        produces a fresh result (roughly every `gait_reassess_every_n_frames`
        frames once its window is full -- see GAIT_WINDOW_FRAMES's own
        comment). Receives
        `{"frame": int, "timestamp": float, "result": <GaitRiskAssessor.
        assess_risk() output, or None>, "torso_baseline": float | None,
        "torso_baseline_mode": "2d" | "3d" | None}`. This is the primary
        integration/instrumentation hook for verifying GAIT is actually
        reachable from this loop (see tests/test_realtime_gait_integration.py)
        and for wiring GAIT's risk score into a dashboard -- per
        docs/IMPLEMENTATION_PLAN.md Section 5.3, it is intentionally a
        SEPARATE, parallel output, never merged into `fall_flags`/
        `alarm_active`/`on_alert`'s own gating logic.

    GAIT integration
    -----------------
    Runs a `StreamingGaitRiskAssessor` alongside the existing posture/LSTM
    fall pipeline, fed the SAME per-frame `row` this loop already builds
    for `classify_posture_and_fall()` (see `build_pose_row`'s own
    `world_landmarks` parameter for how MediaPipe's `pose_world_landmarks`
    -- already computed by the SAME `detect_for_video()` call as the 2D
    landmarks, previously discarded -- is threaded through). A
    `TorsoBaselineCalibrator` watches the stream of
    `classify_posture_and_fall()` verdicts already being computed for the
    fall decision and, the FIRST time it sees a long enough confirmed-
    Standing, non-fall run, establishes a one-time session torso-length
    baseline and hands it to the assessor via `set_torso_baseline()` --
    this is what makes the walking_speed/stride_regularity/postural_sway
    torso-collapse protections (see gait_features.MIN_TORSO_BASELINE_RATIO's
    docstring) actually reachable in a live session, not just in unit
    tests (previously, nothing in this repository ever supplied
    `_torso_baseline`, so those protections -- though correctly
    implemented and tested -- were inert in every runnable path; see
    docs/GAIT_DATA_ASSESSMENT.md Section 9.2 for the audit finding this
    closes). GAIT's own output (`risk_score`, per-signal detail) is
    surfaced via `on_gait_update` and the on-screen overlay ONLY -- it
    never feeds `fall_detected`/the debounced alarm, matching the existing
    "additive, not gating" pattern this file already uses for
    `object_detector` (see that variable's own comment below).
    """
    detector = _make_detector()
    lstm = _load_lstm(use_lstm)
    object_detector = _load_object_detector(use_objects, object_model_path, object_conf, object_imgsz)
    gait_assessor, gait_calibrator = _load_gait(
        use_gait, gait_window_frames, gait_reassess_every_n_frames, gait_min_calibration_frames)

    cap = cv2.VideoCapture(input_source)
    if not cap.isOpened():
        detector.close()
        raise RuntimeError(f"Cannot open input source: {input_source}")

    # Fresh inter-frame state for this session (critical: clears any state left
    # over from a previous run inside the same process).
    reset_session_state()

    previous_rows = []
    fall_flags = deque(maxlen=alert_window)   # recent per-frame hybrid fall flags
    alarm_active = False
    alarm_until = 0.0
    frame_count = 0
    fps_ema = None
    last_t = time.time()
    t_start = last_t   # base for the monotonic VIDEO-mode timestamp
    latest_gait_result = None   # most recent non-None GAIT assess_risk() output, for overlay/on_alert context

    print("[realtime] Started. Press 'q' in the window (or Ctrl+C) to quit.")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[realtime] End of stream / camera read failed.")
                break
            frame_count += 1
            now = time.time()

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            # VIDEO mode needs a monotonically increasing millisecond timestamp.
            result = detector.detect_for_video(mp_image, int((now - t_start) * 1000))

            landmarks, visibility, world_landmarks = [], [], []
            if result.pose_landmarks:
                landmarks = [(lm.x, lm.y) for lm in result.pose_landmarks[0]]
                # Carry MediaPipe's own per-joint confidence through. Without it
                # the pipeline cannot tell a joint that was SEEN from one that was
                # GUESSED behind furniture, and guessed joints are what produce
                # phantom "Lying"/fall readings.
                visibility = [lm.visibility for lm in result.pose_landmarks[0]]
            if result.pose_world_landmarks:
                # MediaPipe's real-world-metric 3D output (x/y/z meters, roughly
                # hip-relative), computed by the SAME detect_for_video() call
                # above -- no extra inference cost. Feeds src/gait/gait_features.py's
                # optional "world_keypoints" row field via build_pose_row's
                # world_landmarks param (see that param's own docstring); every
                # OTHER consumer of `row` (posture/fall classification, LSTM)
                # ignores this entirely.
                world_landmarks = [(lm.x, lm.y, lm.z) for lm in result.pose_world_landmarks[0]]

            # Wall-clock timestamp so _compute_velocity's dt is the true elapsed
            # inter-frame time (correct for a live feed with variable frame rate).
            row = build_pose_row(timestamp=str(now), frame=frame_count, landmarks=landmarks,
                                 visibility=visibility or None,
                                 min_visibility=min_visibility,
                                 world_landmarks=world_landmarks or None)
            result_dict = classify_posture_and_fall(row, previous_rows=previous_rows,
                                                    lstm_classifier=lstm)
            row.update(result_dict)
            previous_rows.append(row)
            if len(previous_rows) > HISTORY_CAP:
                previous_rows = previous_rows[-HISTORY_CAP:]

            posture = result_dict.get("posture_label", "Unknown")
            fall_now = bool(result_dict.get("fall_detected", False))
            fall_flags.append(1 if fall_now else 0)

            # ── GAIT (separate, parallel risk signal -- never gates fall_flags) ──
            # Wrapped defensively: a bug in GAIT must never be able to stall or
            # crash the fall-detection loop it rides alongside (same standard
            # object_detector is already held to just below).
            if gait_assessor is not None:
                try:
                    if gait_calibrator is not None and not gait_calibrator.is_calibrated:
                        if gait_calibrator.observe(row, posture, fall_now):
                            gait_assessor.set_torso_baseline(gait_calibrator.baseline)
                            print(f"[realtime] GAIT torso baseline established "
                                  f"({gait_calibrator.baseline_mode}-mode, "
                                  f"{gait_calibrator.baseline:.4f}) at frame {frame_count}.")
                    gait_result = gait_assessor.push_frame(row)
                    if gait_result is not None:
                        latest_gait_result = gait_result
                        if on_gait_update is not None:
                            on_gait_update({
                                "frame": frame_count,
                                "timestamp": now,
                                "result": gait_result,
                                "torso_baseline": gait_calibrator.baseline if gait_calibrator else None,
                                "torso_baseline_mode": gait_calibrator.baseline_mode if gait_calibrator else None,
                            })
                except Exception as e:
                    print(f"[realtime] GAIT assessment error (frame {frame_count}): {e}")

            # Object detection runs alongside pose, not instead of it -- purely
            # additive context (what furniture/objects are in view). It never
            # feeds fall_detected above; the alarm stays posture/LSTM-only.
            objects = object_detector.detect(frame) if object_detector is not None else []

            # ── Debounced alert decision ────────────────────────────────────
            hits = sum(fall_flags)
            if not alarm_active and hits >= alert_min_hits:
                alarm_active = True
                alarm_until = now + alert_hold
                event = {
                    "frame": frame_count,
                    "timestamp": now,
                    "posture": posture,
                    "labels": result_dict.get("other_labels", ""),
                    # Contextual only -- GAIT never influenced this alert firing
                    # (see the "GAIT integration" note in this function's own
                    # docstring). None if GAIT hasn't produced a result yet
                    # (e.g. still filling its window) or is disabled.
                    "gait_risk_score": latest_gait_result["risk_score"] if latest_gait_result else None,
                }
                print(f"\n*** FALL ALERT *** frame={frame_count} posture={posture} "
                      f"labels={event['labels']}  ({hits}/{alert_window} recent frames)\n")
                if on_alert is not None:
                    try:
                        on_alert(event)
                    except Exception as e:
                        print(f"[realtime] on_alert callback error: {e}")
            elif alarm_active and now >= alarm_until and hits == 0:
                # Re-arm only after the hold elapses AND the person is no longer
                # being flagged (avoids flapping while they are still down).
                alarm_active = False

            # ── FPS (EMA) ───────────────────────────────────────────────────
            dt = now - last_t
            last_t = now
            if dt > 0:
                inst = 1.0 / dt
                fps_ema = inst if fps_ema is None else 0.9 * fps_ema + 0.1 * inst

            if show_display:
                if show_skeleton:
                    _draw_skeleton(frame, landmarks, visibility, min_visibility)
                _draw_objects(frame, objects)
                _draw_overlay(frame, posture, fall_now, alarm_active, fps_ema, hits, alert_window)
                _draw_gait(frame, latest_gait_result, gait_calibrator)
                try:
                    cv2.imshow("S.A.G.E. Real-Time Fall Detection", frame)
                    if (cv2.waitKey(1) & 0xFF) in (ord("q"), ord("Q")):
                        print("[realtime] Quit requested.")
                        break
                except cv2.error:
                    show_display = False  # headless environment; keep processing
    except KeyboardInterrupt:
        print("\n[realtime] Interrupted by user.")
    finally:
        cap.release()
        detector.close()
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            pass
        print(f"[realtime] Stopped after {frame_count} frames.")


def _draw_objects(frame, objects):
    """Draw YOLO's furniture/person boxes. Purely visual context -- these boxes
    never influence the fall_detected decision, which stays posture/LSTM-only."""
    if not objects:
        return
    blue = (255, 160, 0)
    for det in objects:
        x1, y1, x2, y2 = (int(v) for v in det["bbox"])
        cv2.rectangle(frame, (x1, y1), (x2, y2), blue, 1, cv2.LINE_AA)
        label = f'{det["class"]} {det["confidence"]:.2f}'
        cv2.putText(frame, label, (x1, max(0, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, blue, 1, cv2.LINE_AA)


def _draw_skeleton(frame, landmarks, visibility=None,
                   min_visibility=MIN_LANDMARK_VISIBILITY):
    """Draw the MediaPipe pose skeleton (joints + bone connections) on frame.

    landmarks: list of (x, y) in normalized [0, 1] coordinates, as built each
    frame in the main loop (empty list if pose detection found no person).

    Joints MediaPipe reports as unreliable (visibility < min_visibility) are
    drawn dim red instead of yellow, and their bones dashed-grey. Those are the
    joints the detector is GUESSING at, and which the pipeline now ignores --
    so what you see on screen is exactly what the fall logic is reasoning over.
    """
    if not landmarks:
        return
    h, w = frame.shape[:2]
    pts = [(int(x * w), int(y * h)) for x, y in landmarks]
    ok = [True] * len(pts)
    if visibility:
        ok = [i < len(visibility) and visibility[i] >= min_visibility
              for i in range(len(pts))]
    cyan, grey = (255, 255, 0), (110, 110, 110)
    yellow, dim_red = (0, 255, 255), (60, 60, 200)
    for a, b in POSE_CONNECTIONS:
        if a < len(pts) and b < len(pts):
            trusted = ok[a] and ok[b]
            cv2.line(frame, pts[a], pts[b], cyan if trusted else grey,
                     2 if trusted else 1, cv2.LINE_AA)
    for i, (x, y) in enumerate(pts):
        cv2.circle(frame, (x, y), 4 if ok[i] else 3,
                   yellow if ok[i] else dim_red, -1, cv2.LINE_AA)


def _draw_overlay(frame, posture, fall_now, alarm_active, fps, hits, window):
    green, red, amber, white = (0, 200, 0), (0, 0, 255), (0, 165, 255), (255, 255, 255)
    posture_color = red if posture == "Lying" else (amber if posture == "Sitting" else green)
    cv2.putText(frame, f"Posture: {posture}", (12, 32),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, posture_color, 2, cv2.LINE_AA)
    if fps is not None:
        cv2.putText(frame, f"{fps:4.1f} FPS", (12, 62),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 1, cv2.LINE_AA)
    cv2.putText(frame, f"fall frames: {hits}/{window}", (12, 88),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, white, 1, cv2.LINE_AA)
    if alarm_active:
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), red, 8)
        cv2.putText(frame, "FALL DETECTED", (int(w * 0.18), int(h * 0.5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, red, 3, cv2.LINE_AA)
    elif fall_now:
        cv2.putText(frame, "fall signal...", (12, 116),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, amber, 2, cv2.LINE_AA)


def _draw_gait(frame, gait_result, gait_calibrator):
    """Purely informational overlay for GAIT's own risk score -- see this
    module's "GAIT integration" docstring note: displayed for visibility
    only, never influences `fall_now`/`alarm_active` drawn by
    `_draw_overlay` just above this call. Shows "warming up" (no result
    yet -- window not full, or calibration not yet established) rather
    than silently drawing nothing, so it's visually obvious GAIT is
    running at all, not merely absent from the frame."""
    white, amber = (255, 255, 255), (0, 165, 255)
    if gait_result is None:
        calib_note = "" if gait_calibrator is None else (
            " (baseline pending)" if not gait_calibrator.is_calibrated else "")
        cv2.putText(frame, f"Gait: warming up{calib_note}", (12, 142),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, white, 1, cv2.LINE_AA)
        return
    score = gait_result.get("risk_score")
    if score is None:
        cv2.putText(frame, "Gait risk: n/a this window", (12, 142),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, white, 1, cv2.LINE_AA)
        return
    color = amber if score >= 0.6 else white
    baseline_note = ""
    if gait_calibrator is not None and gait_calibrator.is_calibrated:
        baseline_note = f"  [baseline: {gait_calibrator.baseline_mode}]"
    cv2.putText(frame, f"Gait risk: {score:.2f}{baseline_note}", (12, 142),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1, cv2.LINE_AA)


def main():
    p = argparse.ArgumentParser(description="S.A.G.E. real-time fall detection")
    p.add_argument("--input", default="0",
                   help="Camera index (e.g. 0) or path to a video file. Default: 0 (webcam).")
    p.add_argument("--no-lstm", action="store_true", help="Disable the LSTM (heuristic only).")
    p.add_argument("--no-display", action="store_true", help="Run headless (no preview window).")
    p.add_argument("--no-skeleton", action="store_true",
                   help="Hide the pose skeleton overlay (shown by default).")
    p.add_argument("--alert-window", type=int, default=ALERT_WINDOW,
                   help=f"Debounce window in frames (default {ALERT_WINDOW}).")
    p.add_argument("--alert-min-hits", type=int, default=ALERT_MIN_HITS,
                   help=f"Fall frames within the window needed to alert (default {ALERT_MIN_HITS}).")
    p.add_argument("--alert-hold", type=float, default=ALERT_HOLD_SECONDS,
                   help=f"Seconds to latch the alarm before re-arming (default {ALERT_HOLD_SECONDS}).")
    p.add_argument("--no-objects", action="store_true",
                   help="Disable YOLO object/furniture detection (pose-only). It never feeds "
                        "the fall alarm either way -- this only turns off the on-screen boxes.")
    p.add_argument("--object-model", type=str, default=str(DEFAULT_OBJECT_MODEL_PATH),
                   help=f"YOLO weights for object detection (default {DEFAULT_OBJECT_MODEL_PATH.name}).")
    p.add_argument("--object-conf", type=float, default=0.25,
                   help="Object-detection confidence threshold (default 0.25 -- 0.4 was found to "
                        "under-detect a person overlapping a bed on the merged v4 model).")
    p.add_argument("--object-imgsz", type=int, default=320,
                   help="Object-detection inference size (default 320, matches training/gating).")
    p.add_argument("--no-gait", action="store_true",
                   help="Disable the GAIT streaming risk assessor. It never feeds the fall alarm "
                        "either way (see docs/IMPLEMENTATION_PLAN.md Section 5.3) -- this only "
                        "turns off the additional gait-risk overlay/computation.")
    args = p.parse_args()

    source = int(args.input) if str(args.input).isdigit() else args.input
    run(
        source,
        use_lstm=not args.no_lstm,
        show_display=not args.no_display,
        show_skeleton=not args.no_skeleton,
        alert_window=args.alert_window,
        alert_min_hits=args.alert_min_hits,
        alert_hold=args.alert_hold,
        use_objects=not args.no_objects,
        object_model_path=Path(args.object_model),
        object_conf=args.object_conf,
        object_imgsz=args.object_imgsz,
        use_gait=not args.no_gait,
    )


if __name__ == "__main__":
    main()
