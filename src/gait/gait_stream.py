"""
gait_stream.py
===============
Streaming/windowed wrapper around GaitRiskAssessor for a SINGLE live camera
feed. GaitRiskAssessor.assess_risk() (see gait_risk.py) takes one
already-built window (a plain list of pose rows) per call -- it has no
concept of "the next frame just arrived." A live camera has no natural
window boundary, so something has to (a) hold a rolling history of recent
frames with bounded memory, and (b) decide *when* that history is worth
re-assessing, without recomputing the full feature set on every single
incoming frame (wasteful: assess_risk() is O(window length) work for
signals -- walking speed, stride regularity, postural sway -- that the
underlying clinical literature already treats as multi-second trends, not
frame-level events). This module is that glue; it does not change
GaitRiskAssessor's own output contract or scoring at all.

Explicitly single-camera. Multi-stream micro-batching (e.g. several camera
feeds sharing one worker pool) is a different problem than what's built
here and is intentionally not attempted -- see GaitPipeline's docstring.

Four pieces, each independently usable:

  RingFrameBuffer
      Fixed-size (deque(maxlen=...)) rolling buffer of pose-row dicts --
      O(1) append, automatic eviction of the oldest frame once full, so
      memory stays bounded across a session of unbounded length instead of
      an ever-growing list.

  StreamingGaitRiskAssessor
      Feeds a frame-by-frame stream into GaitRiskAssessor on a controlled
      CADENCE (re-assess every `reassess_every_n_frames` new frames, not
      every one) once the buffer is full. Single-threaded, synchronous --
      call `push_frame()` directly from wherever frames arrive if you don't
      need the producer/consumer decoupling below.

  TorsoBaselineCalibrator
      Watches a stream of (pose row, posture_label, fall_detected) triples
      -- the SAME per-frame classification a real-time caller is already
      computing for its own fall decision -- and, the first time it sees a
      long enough confirmed-Standing, non-fall run, establishes the one-time
      session torso-length reference `StreamingGaitRiskAssessor.
      set_torso_baseline()` needs. See its own docstring for the full safety
      rationale (why THIS signal, not a new independently-tuned one).

  GaitPipeline
      A lightweight producer-consumer wrapper around
      StreamingGaitRiskAssessor: ONE background thread pulls frames off a
      small bounded queue and drives it, so a live capture/MediaPipe loop
      (the producer, on the caller's own thread) never blocks on gait-risk
      computation (the consumer). Deliberately just `threading`, not
      `multiprocessing`: MediaPipe's own inference (C++) and the vectorized
      numpy work in gait_features.py both release the GIL for the bulk of
      their execution, so a second Python thread genuinely runs
      concurrently with the capture/MediaPipe thread for most of the work
      each does -- without multiprocessing's cost (pickling every frame
      across a process boundary, a second Python interpreter's memory
      footprint), which matters on a Jetson Nano's 4 shared cores and
      limited RAM. The same class works unchanged on a Jetson Orin;
      reaching for more concurrency there (e.g. a process pool) is
      realistically only worth it if profiling on that hardware shows this
      one background thread itself is the bottleneck -- unlikely given
      assess_risk() now runs in ~2ms end-to-end for a 150-frame window (see
      benchmarks/profile_gait_pipeline.py).

WIRED IN (a later session): `StreamingGaitRiskAssessor` (driven synchronously
-- `push_frame()` called directly from the frame loop, not through
`GaitPipeline`'s threaded wrapper below) is now the GAIT component
`realtime_fall_detection.py`'s own `run()` actually constructs and feeds
every frame, per docs/IMPLEMENTATION_PLAN.md Section 5.3's own description
of GAIT as "a separate, parallel output ... wired into a dashboard/alert
system as its own independent signal" -- see that function's own "GAIT
integration" docstring for the full data flow, and
docs/GAIT_DATA_ASSESSMENT.md's own later section for the audit finding this
closes (the torso-baseline/3D-world-landmark protections below were, before
this, unreachable from any runnable path in this repository outside unit
tests). `GaitPipeline`'s own threaded producer/consumer wrapper is NOT used
by that integration (a synchronous call was judged sufficient given
assess_risk()'s own measured ~2-6ms cost against a real camera's ~33ms
frame budget -- see `_load_gait`'s own comment in realtime_fall_detection.py)
-- it remains available, tested, and documented below for a future session
that profiles a real deployment and finds the synchronous call is actually
a bottleneck, but is not itself wired into anything today.
`TorsoBaselineCalibrator` (below, alongside `RingFrameBuffer`/
`StreamingGaitRiskAssessor`/`GaitPipeline`) is what establishes the
session-level torso-length reference `StreamingGaitRiskAssessor.
set_torso_baseline()` accepts, from the real-time pipeline's own already-
computed posture classification -- see that class's own docstring.
"""

import queue
import threading
from collections import deque
from typing import Any, Callable, Deque, Dict, List, Optional

from src.gait import gait_features as gf
from src.gait.gait_risk import GaitRiskAssessor


class RingFrameBuffer:
    """Fixed-size rolling buffer of pose-row dicts (see
    pipeline_utils.build_pose_row for the row schema). O(1) append; the
    oldest frame is evicted automatically once `maxlen` is reached --
    bounded memory for a session of unbounded length, instead of a list
    that grows for as long as the camera keeps running."""

    def __init__(self, maxlen: int):
        if maxlen < gf.MIN_WINDOW_FRAMES:
            raise ValueError(
                f"RingFrameBuffer(maxlen={maxlen}): must be >= gait_features.MIN_WINDOW_FRAMES "
                f"({gf.MIN_WINDOW_FRAMES}) -- assess_risk() can never run on a buffer smaller than that."
            )
        self._buf: Deque[dict] = deque(maxlen=maxlen)

    def append(self, row: dict) -> None:
        self._buf.append(row)

    def is_full(self) -> bool:
        return len(self._buf) == self._buf.maxlen

    def __len__(self) -> int:
        return len(self._buf)

    def snapshot(self) -> List[dict]:
        """A plain list copy of the current buffer contents, in
        chronological order -- what GaitRiskAssessor.assess_risk() expects
        as its `window` argument. A copy (not a view onto the live deque)
        so the returned window is a stable snapshot even if more frames
        are appended to the buffer immediately afterward.

        ALIASING NOTE (see docs/GAIT_CODE_REVIEW.md finding #13): this is a
        SHALLOW copy -- a new list, but the SAME row-dict/keypoints-array
        objects the live buffer still holds. Appending to (or evicting
        from) the buffer after calling this is safe (that only affects the
        deque's own list of references, not the objects themselves, so an
        already-taken snapshot's contents are unaffected -- see
        test_snapshot_is_a_stable_copy in tests/test_gait_stream.py). What
        is NOT safe: a caller MUTATING a row dict or its 'keypoints' array
        IN PLACE after getting it from a snapshot -- that mutation would be
        visible through any OTHER reference to the same row, including the
        one still sitting in the live buffer if that row hasn't been
        evicted yet. No caller in this codebase does this today (assess_risk
        and everything it calls only reads from `window`, never mutates
        it), so a deep copy here would be pure defensive overhead with no
        current bug to justify it -- this note exists so a future caller
        knows not to introduce one."""
        return list(self._buf)


class TorsoBaselineCalibrator:
    """Establishes a ONE-TIME, session-level torso-length reference for
    StreamingGaitRiskAssessor.set_torso_baseline() (see that method's and
    gait_features.compute_torso_baseline()'s own docstrings for what the
    value is used for), from a run of frames the CALLER has already judged
    safe to calibrate from -- deliberately NOT derived here from raw pose
    geometry alone.

    WHY THIS RELIES ON THE CALLER'S OWN POSTURE CLASSIFICATION rather than
    inventing a second "is this person standing" detector inside the GAIT
    module: `gait_features.py` has no existing concept of "standing" (its
    own compute_sit_to_stand's hip-angle state machine is a DIFFERENT,
    narrower thing -- a transition detector, not a general posture
    classifier -- see that module's own docstring on the deliberate,
    disclosed divergence from pipeline_utils.py's classifier). The calling
    pipeline (see realtime_fall_detection.py) already runs a classifier
    that decides "Standing" vs. "Sitting" vs. "Lying" vs. "Fall" every
    frame, specifically tuned and validated for that job -- reusing its
    verdict is far more defensible than re-deriving a second, independently
    -tuned "standing" signal inside a module whose whole point is to stay
    decoupled from that classifier's internals (see gait_risk.py's own
    docstring: GAIT is conceptually distinct from the Fall/Lying/Sitting/
    Standing/Unknown classifiers, not a wrapper around one) -- but SAFETY
    gating (this class's entire purpose) is a different concern from
    conceptual independence, and there is no principled reason to ignore a
    signal this trustworthy just to preserve that separation.

    SAFETY, by construction, not by a new ad-hoc check:
      - Only ever accumulates frames while `posture_label == "Standing"`
        AND `fall_detected` is False -- a single frame that is anything
        else (Sitting, Lying, Unknown, Fall, or a fall-flagged Standing
        frame) discards the run-so-far and starts over. This directly
        implements the audit's own requirement ("prevent the baseline from
        being established during an unsuitable state such as a fall, deep
        bend, severe pose-estimation failure, or unstable initialization")
        using the SAME state signal the rest of the pipeline already trusts
        for exactly this kind of judgment, rather than a second, redundant
        one.
      - Requires a CONTIGUOUS run of `min_run_frames` such frames (default
        60, ~2s at 30fps) before even attempting calibration -- a single
        noisy "Standing" frame during camera startup/subject-entering-frame
        jitter cannot trigger this by itself, matching the same
        consecutive-frame-confirmation philosophy already used throughout
        this project (see gait_features._STATE_CONFIRM_FRAMES's own
        docstring for the precedent).
      - The actual value comes from gait_features.compute_torso_baseline(),
        which performs its OWN internal least-noisy-20-frame-sub-segment
        search within whatever candidate run is handed to it and returns
        None (not a bad number) if it can't find one with enough valid
        landmark coverage -- severe pose-estimation failure during an
        otherwise-genuine standing run is therefore caught by that existing,
        already-validated mechanism, not a new one invented here. This
        class enforces `min_run_frames` at least
        `gait_features.CALIBRATION_SEGMENT_FRAMES` so that search always
        has genuine room to work with, never just the bare minimum.
      - Prefers 3D (`_world_raw`) mode automatically whenever the candidate
        run has sufficient world-landmark coverage (see
        gait_features._has_sufficient_world_coverage) -- `compute_torso_
        baseline` itself decides this per call; this class only forwards
        whatever `_world_raw` it was given, exactly as the ambulation/sway
        gates already do.

    Calibrates EXACTLY ONCE per instance (mirrors compute_torso_baseline's
    own "compute ONCE, reuse for every subsequent window" contract, and
    keeps this component's behavior simple and easy to reason about) --
    once `is_calibrated` is True, `observe()` is a no-op that always
    returns False. Construct a fresh instance (the same way
    realtime_fall_detection.py already constructs a fresh detector/LSTM/
    object-detector per `run()` call) for a new session; there is no
    separate `reset()` needed for that reason, though one is provided for a
    caller that wants to force recalibration within a single already-running
    session without discarding other state.
    """

    def __init__(self, min_run_frames: int = 60):
        self._min_run_frames = max(int(min_run_frames), gf.CALIBRATION_SEGMENT_FRAMES)
        self._candidate_run: List[dict] = []
        self.baseline: Optional[float] = None
        self.baseline_mode: Optional[str] = None  # "3d" | "2d", set only once calibrated

    @property
    def is_calibrated(self) -> bool:
        return self.baseline is not None

    def reset(self) -> None:
        """Discard any in-progress candidate run AND any already-established
        baseline, allowing this instance to calibrate again from scratch.
        Not called automatically by anything in this module -- a caller
        that wants a full reset between sessions should simply construct a
        new TorsoBaselineCalibrator instead (see this class's own
        docstring); this method exists for a caller that has an
        independent reason to distrust an already-established baseline
        mid-session (e.g. a detected camera move) without tearing down
        everything else."""
        self._candidate_run = []
        self.baseline = None
        self.baseline_mode = None

    def observe(self, row: dict, posture_label: str, fall_detected: bool) -> bool:
        """Feed one more frame's pose row AND the calling pipeline's own
        classification of it. Returns True on the EXACT call that causes
        calibration to complete (so a caller knows to read `self.baseline`
        and thread it into StreamingGaitRiskAssessor.set_torso_baseline()
        right then) -- False on every other call, including every call
        after calibration has already happened once.

        `row`: the same pose-row dict shape GaitRiskAssessor consumes
        (`{"timestamp", "keypoints", ...}`, optionally `"world_keypoints"`).
        `posture_label`/`fall_detected`: this frame's own verdict from the
        pipeline's existing classifier (e.g. `classify_posture_and_fall()`'s
        result, already computed by the caller for its own purposes -- not
        recomputed here)."""
        if self.is_calibrated:
            return False

        safe = (posture_label == "Standing") and not fall_detected
        if not safe:
            if self._candidate_run:
                self._candidate_run = []
            return False

        self._candidate_run.append(row)
        if len(self._candidate_run) < self._min_run_frames:
            return False

        raw = gf._raw_keypoint_array(self._candidate_run)
        world_raw = gf._raw_world_keypoint_array(self._candidate_run)
        baseline = gf.compute_torso_baseline(self._candidate_run, _raw=raw, _world_raw=world_raw)
        if baseline is None:
            # A full-length, posture-confirmed-safe run, but not enough
            # VALID landmark coverage within it to trust a number (e.g.
            # heavy occlusion during an otherwise-genuine standing hold) --
            # keep sliding forward instead of giving up permanently: drop
            # only the oldest frame so the next observe() call re-attempts
            # with one new frame rather than restarting the full wait.
            self._candidate_run = self._candidate_run[-(self._min_run_frames - 1):]
            return False

        self.baseline = baseline
        self.baseline_mode = "3d" if gf._has_sufficient_world_coverage(world_raw) else "2d"
        self._candidate_run = []
        return True


class StreamingGaitRiskAssessor:
    """Feeds a live, frame-by-frame stream into GaitRiskAssessor on a
    controlled cadence instead of recomputing on every single frame.

    `window_frames`: how many trailing frames each assessment covers (must
    be >= gait_features.MIN_WINDOW_FRAMES).
    `reassess_every_n_frames`: minimum number of new frames between
    assessments once the buffer is full -- default 15 (~0.5s at 30fps) is a
    reasonable middle ground between staleness and wasted recompute; tune
    to your actual camera fps / CPU budget. Reassessing on every frame
    (reassess_every_n_frames=1) is allowed and still correct, just wasteful
    given how slowly these signals actually move.
    """

    def __init__(self, window_frames: int = 150, reassess_every_n_frames: int = 15,
                 assessor: Optional[GaitRiskAssessor] = None):
        self._buffer = RingFrameBuffer(maxlen=window_frames)
        self._assessor = assessor if assessor is not None else GaitRiskAssessor()
        self._reassess_every_n_frames = max(1, int(reassess_every_n_frames))
        self._frames_since_last_assessment = 0
        # See set_torso_baseline()'s own docstring. None (the default, and
        # the value for every caller that never calls set_torso_baseline)
        # preserves this class's original behavior exactly -- assess_risk()
        # itself already treats _torso_baseline=None as "don't gate."
        self._torso_baseline: Optional[float] = None

    def set_torso_baseline(self, torso_baseline: Optional[float]) -> None:
        """Establish (or clear, by passing None) the session-level
        confirmed-standing torso-length reference threaded into every
        SUBSEQUENT assess_risk() call this instance makes (see
        GaitRiskAssessor.assess_risk()'s own `_torso_baseline` docstring,
        and gait_features.MIN_TORSO_BASELINE_RATIO's docstring for what it
        protects against: a sustained torso-length collapse, e.g. a deep
        bend, fabricating an implausible walking_speed/stride_regularity/
        postural_sway reading).

        Deliberately a separate, explicit, MUTABLE setter rather than a
        constructor-only parameter: this class is typically constructed
        BEFORE a caller has observed enough of the stream to establish a
        trustworthy baseline (see gait_stream.TorsoBaselineCalibrator, the
        intended real-time source of the value passed here) -- forcing the
        baseline through `__init__` would mean either delaying construction
        until calibration completes (losing every frame in between, since
        `RingFrameBuffer` needs to start filling immediately) or passing a
        placeholder and mutating it anyway. A plain setter avoids both.

        Does NOT retroactively change any assess_risk() call already made,
        and does NOT clear or otherwise touch the frame buffer -- frames
        already buffered before calibration completes are used in the next
        assessment exactly as they would be without this call; only the gate
        applied AT assessment time changes. Call with None to revert to this
        class's original (ungated) behavior, e.g. if a caller decides a
        previously-established baseline is no longer trustworthy (a full
        session reset, however, should construct a fresh instance instead --
        see this class's own single-baseline-per-instance convention, which
        matches gait_features.compute_torso_baseline()'s own "compute ONCE
        per session, reuse for every subsequent window" contract)."""
        self._torso_baseline = torso_baseline

    def push_frame(self, row: dict) -> Optional[Dict[str, Any]]:
        """Append one new frame. Returns a fresh assess_risk() result if
        the buffer is full AND the reassessment cadence has elapsed;
        otherwise returns None without doing any assess_risk() work (the
        common case for most incoming frames)."""
        self._buffer.append(row)
        self._frames_since_last_assessment += 1

        if not self._buffer.is_full():
            return None
        if self._frames_since_last_assessment < self._reassess_every_n_frames:
            return None

        self._frames_since_last_assessment = 0
        window = self._buffer.snapshot()
        return self._assessor.assess_risk(window, _torso_baseline=self._torso_baseline)


class GaitPipeline:
    """Producer-consumer decoupling for a single live camera: a capture/
    MediaPipe loop (the producer, on the caller's own thread) calls
    `submit_frame()`, which never blocks; ONE background thread (the
    consumer) pulls frames off a small bounded queue and drives a
    StreamingGaitRiskAssessor.

    Deliberately ONE consumer thread, not a pool: this is a single-camera
    prototype with a single risk stream to maintain, not a multi-stream
    micro-batching problem -- extending to multiple cameras later would
    mean one GaitPipeline per camera feed (each with its own
    thread/buffer), not more concurrency inside this class.

    `queue_maxsize`: small and bounded on purpose (default 4, ~130ms of
    frames at 30fps). If the consumer ever falls behind -- shouldn't
    happen given assess_risk()'s measured ~2ms cost, but robustness matters
    more than a perfect guarantee here -- the oldest queued frame is
    dropped rather than letting the queue (and therefore memory and
    latency) grow unboundedly. Dropping a few frames costs essentially
    nothing for THIS signal: gait risk is a multi-second trend, not a
    per-frame-critical one, unlike the separate fall-detection alert path
    (see realtime_fall_detection.py's own debounce logic), which this
    module does not touch or replace.

    Usage sketch (illustrative only -- not wired into any live capture
    script here; see this module's docstring for why):
        pipeline = GaitPipeline(on_result=lambda r: print(r["risk_score"]))
        pipeline.start()
        while camera_running:
            row = build_pose_row(...)   # from your MediaPipe capture loop
            pipeline.submit_frame(row)  # non-blocking
        pipeline.stop()
    """

    def __init__(self, window_frames: int = 150, reassess_every_n_frames: int = 15,
                 queue_maxsize: int = 4, on_result: Optional[Callable[[Dict[str, Any]], None]] = None,
                 assessor: Optional[GaitRiskAssessor] = None):
        self._queue: "queue.Queue[dict]" = queue.Queue(maxsize=queue_maxsize)
        self._streaming_assessor = StreamingGaitRiskAssessor(
            window_frames=window_frames,
            reassess_every_n_frames=reassess_every_n_frames,
            assessor=assessor,
        )
        self._on_result = on_result
        self._latest_result: Optional[Dict[str, Any]] = None
        self._latest_result_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread is not None:
            return  # already running
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="GaitPipelineConsumer", daemon=True)
        self._thread.start()

    def stop(self, timeout: Optional[float] = 2.0) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None

    def submit_frame(self, row: dict) -> bool:
        """Non-blocking: enqueues one pose row for the consumer thread to
        pick up. Returns False if the consumer is currently behind (the
        oldest queued frame is dropped to make room) -- this call NEVER
        blocks the calling (producer/capture) thread, which is the entire
        point of this class."""
        try:
            self._queue.put_nowait(row)
            return True
        except queue.Full:
            try:
                self._queue.get_nowait()  # drop the oldest queued frame
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(row)
            except queue.Full:
                pass
            return False

    def get_latest_result(self) -> Optional[Dict[str, Any]]:
        """Non-blocking read of the most recent assess_risk() result (or
        None if none has been produced yet)."""
        with self._latest_result_lock:
            return self._latest_result

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                row = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            result = self._streaming_assessor.push_frame(row)
            if result is not None:
                with self._latest_result_lock:
                    self._latest_result = result
                if self._on_result is not None:
                    self._on_result(result)
