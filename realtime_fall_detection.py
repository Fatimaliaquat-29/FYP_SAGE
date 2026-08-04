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

POSE_MODEL_PATH = str(REPO_ROOT / "models" / "pose_landmarker_full.task")

# ── Alert debounce defaults ────────────────────────────────────────────────
ALERT_WINDOW      = 12    # look at the last N frames
ALERT_MIN_HITS    = 4     # need this many fall-flagged frames within the window
ALERT_HOLD_SECONDS = 5.0  # keep the alarm latched this long before it can re-arm

# Cap on retained history. The heuristic's dynamic calibration scans up to the
# last ~300 Standing frames, and the LSTM needs window_size+1; 320 covers both
# while keeping a long-running session's memory bounded.
HISTORY_CAP = 320

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


def run(input_source, use_lstm=True, show_display=True, show_skeleton=True,
        alert_window=ALERT_WINDOW, alert_min_hits=ALERT_MIN_HITS,
        alert_hold=ALERT_HOLD_SECONDS, on_alert=None,
        min_visibility=MIN_LANDMARK_VISIBILITY):
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
    """
    detector = _make_detector()
    lstm = _load_lstm(use_lstm)

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

            landmarks, visibility = [], []
            if result.pose_landmarks:
                landmarks = [(lm.x, lm.y) for lm in result.pose_landmarks[0]]
                # Carry MediaPipe's own per-joint confidence through. Without it
                # the pipeline cannot tell a joint that was SEEN from one that was
                # GUESSED behind furniture, and guessed joints are what produce
                # phantom "Lying"/fall readings.
                visibility = [lm.visibility for lm in result.pose_landmarks[0]]

            # Wall-clock timestamp so _compute_velocity's dt is the true elapsed
            # inter-frame time (correct for a live feed with variable frame rate).
            row = build_pose_row(timestamp=str(now), frame=frame_count, landmarks=landmarks,
                                 visibility=visibility or None,
                                 min_visibility=min_visibility)
            result_dict = classify_posture_and_fall(row, previous_rows=previous_rows,
                                                    lstm_classifier=lstm)
            row.update(result_dict)
            previous_rows.append(row)
            if len(previous_rows) > HISTORY_CAP:
                previous_rows = previous_rows[-HISTORY_CAP:]

            posture = result_dict.get("posture_label", "Unknown")
            fall_now = bool(result_dict.get("fall_detected", False))
            fall_flags.append(1 if fall_now else 0)

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
                _draw_overlay(frame, posture, fall_now, alarm_active, fps_ema, hits, alert_window)
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
    )


if __name__ == "__main__":
    main()
