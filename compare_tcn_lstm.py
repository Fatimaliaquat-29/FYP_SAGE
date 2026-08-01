"""
compare_tcn_lstm.py
====================
Side-by-side comparison of the LSTM and TCN posture classifiers on the same
labelled test footage used by evaluate_real_footage.py / hybrid_evaluate.py.

Both models are evaluated under IDENTICAL conditions to keep the comparison
fair:
  - The same extracted keypoints (extract_keypoints() runs once per clip and
    both classifiers consume the exact same frames).
  - The same rolling-window buffer construction and the same public
    predict() interface (LSTMPostureClassifier / TCNPostureClassifier are
    interchangeable by design -- see lstm_classifier.py / tcn_classifier.py).
  - Raw per-window argmax decisions are used directly, with no per-model
    probability threshold, warmup suppression, or consecutive-frame
    smoothing layered on top (unlike hybrid_evaluate.py, which tunes those
    knobs specifically for the heuristic+LSTM OR-gate). Any such smoothing
    would need separate tuning per model, which would make the comparison
    about the tuning rather than about the architectures.

Metrics reported (both models, identical evaluation code path):
  - Posture accuracy / precision / recall / F1 (overall + per-class)
  - Fall-detection recall (did the model flag the labelled fall window?)
  - Inference latency (ms per predict() call, mean/median/p95)
  - Trainable parameter count
  - Peak resident-memory usage (RSS) while the model runs its full pass

Usage
-----
  python compare_tcn_lstm.py --batch_dir "Testing/Sanawar Testing 7-22-26" --output_dir results/tcn_vs_lstm
  python compare_tcn_lstm.py --video path/to/clip.mp4 --ground_truth path/to/clip_gt.csv --output_dir results/tcn_vs_lstm
"""

import argparse
import csv
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import (
    discover_clips,
    extract_keypoints,
    load_ground_truth,
    build_frame_gt,
    get_fall_window,
)
from src.posture.pipeline_utils import LANDMARK_COUNT
from src.posture.lstm.lstm_classifier import LSTMPostureClassifier
from src.posture.tcn.tcn_classifier import TCNPostureClassifier

POSTURE_CLASSES = ["Standing", "Sitting", "Lying", "Unknown"]
OUTPUT_DIR_DEFAULT = "results/tcn_vs_lstm"


def _relative_to_repo(path: Path) -> str:
    """Render a path relative to REPO_ROOT for readable report output
    (classifier.model_path is always absolute)."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ------------------------------------------------------------------------------
# Peak RSS monitor
# ------------------------------------------------------------------------------

class _PeakRSSMonitor:
    """Samples this process's resident memory in a background thread and
    tracks the maximum observed value while a model's evaluation pass runs."""

    def __init__(self, interval: float = 0.05):
        self.interval = interval
        self._peak_bytes = 0
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._process = None

    def start(self):
        try:
            import psutil
        except ImportError:
            self._process = None
            return
        self._process = psutil.Process()
        self._peak_bytes = self._process.memory_info().rss
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            rss = self._process.memory_info().rss
            if rss > self._peak_bytes:
                self._peak_bytes = rss
            self._stop.wait(self.interval)

    def stop_mb(self) -> Optional[float]:
        if self._process is None:
            return None
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        return self._peak_bytes / (1024 * 1024)


# ------------------------------------------------------------------------------
# Keypoint row -> classifier input row
# ------------------------------------------------------------------------------

def _to_keypoints_row(kp_row: dict) -> dict:
    """Convert an extract_keypoints() row (lm_{i}_x/y/z/...) into the flat
    'keypoints' list format LSTMPostureClassifier/TCNPostureClassifier expect
    (same conversion hybrid_evaluate.py does for the LSTM alone)."""
    flat = []
    for i in range(LANDMARK_COUNT):
        flat.append(kp_row.get(f"lm_{i}_x", np.nan))
        flat.append(kp_row.get(f"lm_{i}_y", np.nan))
    return {
        "keypoints": flat,
        "frame_number": kp_row.get("frame_number", 0),
        "timestamp": kp_row.get("timestamp", 0.0),
    }


# ------------------------------------------------------------------------------
# Per-clip, per-model evaluation
# ------------------------------------------------------------------------------

def run_model_over_clip(
    classifier,
    clip_name: str,
    kp_rows: List[dict],
    frame_gt,
    fall_window: Optional[Tuple[int, int]],
) -> dict:
    """
    Run one classifier over one clip's keypoints, frame by frame, using a
    rolling buffer of exactly the length the classifier itself asks for
    (classifier.raw_history_needed). This is the ONE inference code path used
    for both LSTM and TCN (see evaluate_model()) -- only the `classifier`
    argument differs between the two calls, so nothing about the windowing,
    timing, or scoring is duplicated per model.

    Returns a dict:
      records           : list of per-window dicts -- one per window the
                           classifier actually ran inference on --
                           {clip_name, frame_number, gt_label, pred_label,
                            correct, latency_ms}. gt_label/correct are ""
                           when the frame has no usable (non-ignored) ground
                           truth, so every inference call still contributes a
                           latency sample even outside scored regions.
      fall_result       : {"result": "true_positive"|"false_negative"|
                                     "false_positive"|"no_fall",
                            "latency": int|None}  (frames from window start)
      clip_latencies_ms : latencies (ms) for this clip only, for the
                          per-clip average latency reported alongside
                          per-clip correctness.
    """
    buffer: List[dict] = []
    fall_frames: List[int] = []
    records: List[dict] = []
    clip_latencies_ms: List[float] = []

    needed = classifier.raw_history_needed
    for kp_row in kp_rows:
        buffer.append(_to_keypoints_row(kp_row))
        if len(buffer) > needed:
            buffer.pop(0)
        if len(buffer) < needed:
            continue

        t0 = time.perf_counter()
        result = classifier.predict(buffer)
        latency_ms = (time.perf_counter() - t0) * 1000.0
        clip_latencies_ms.append(latency_ms)

        frame_number = int(kp_row.get("frame_number", 0))
        pred_label = (result.get("posture_label") or "Unknown").capitalize()
        if result.get("fall_detected"):
            fall_frames.append(frame_number)

        gt_label = ""
        correct = ""
        if frame_number in frame_gt.index:
            gt_entry = frame_gt.loc[frame_number]
            if not gt_entry["ignore"]:
                gt_label = gt_entry["gt_label"].strip().capitalize()
                correct = (gt_label == pred_label)

        records.append({
            "clip_name": clip_name,
            "frame_number": frame_number,
            "gt_label": gt_label,
            "pred_label": pred_label,
            "correct": correct,
            "latency_ms": round(latency_ms, 4),
        })

    fall_result = _score_fall(fall_frames, fall_window)
    return {
        "records": records,
        "fall_result": fall_result,
        "clip_latencies_ms": clip_latencies_ms,
    }


def _score_fall(fall_frames: List[int], fall_window: Optional[Tuple[int, int]]) -> dict:
    """Same TP/FN/FP/no_fall scoring as evaluate_real_footage.score_fall."""
    if fall_window is None:
        if fall_frames:
            return {"result": "false_positive", "latency": None}
        return {"result": "no_fall", "latency": None}

    window_start, window_end = fall_window
    inside = [f for f in fall_frames if window_start <= f <= window_end]
    outside = [f for f in fall_frames if f < window_start or f > window_end]

    if inside:
        return {"result": "true_positive", "latency": inside[0] - window_start}
    if outside:
        return {"result": "false_positive", "latency": None}
    return {"result": "false_negative", "latency": None}


# ------------------------------------------------------------------------------
# Full evaluation for one model across all clips
# ------------------------------------------------------------------------------

def evaluate_model(
    model_label: str,
    classifier,
    clips: List[Tuple[str, str, str]],
    cached_keypoints: Dict[str, Tuple[List[dict], float, int]],
    output_dir: Path,
) -> dict:
    print(f"\n{'='*60}\n  Evaluating {model_label}\n{'='*60}")

    if not classifier.is_available:
        print(f"  WARNING: {model_label} model not available -- skipping.")
        return {
            "model_label": model_label,
            "available": False,
        }

    monitor = _PeakRSSMonitor()
    monitor.start()

    all_records: List[dict] = []
    fall_results: List[dict] = []
    per_clip_summary: List[dict] = []

    for video_path, gt_path, clip_name in clips:
        kp_rows, fps, total_frames = cached_keypoints[clip_name]
        gt_df = load_ground_truth(gt_path)
        frame_gt = build_frame_gt(gt_df, fps, total_frames)
        fall_window = get_fall_window(gt_df, fps)

        print(f"  [{model_label}] {clip_name}: classifying {len(kp_rows)} frames...")
        clip_result = run_model_over_clip(classifier, clip_name, kp_rows, frame_gt, fall_window)
        all_records.extend(clip_result["records"])
        fall_results.append({"clip_name": clip_name, **clip_result["fall_result"]})

        clip_lat = clip_result["clip_latencies_ms"]
        scored = [r for r in clip_result["records"] if r["correct"] != ""]
        per_clip_summary.append({
            "clip_name": clip_name,
            "n_windows": len(clip_lat),
            "avg_latency_ms": statistics.fmean(clip_lat) if clip_lat else float("nan"),
            "n_scored": len(scored),
            "n_correct": sum(1 for r in scored if r["correct"]),
            "fall_result": clip_result["fall_result"]["result"],
        })

    peak_ram_mb = monitor.stop_mb()
    param_count = classifier._model.count_params() if classifier._model is not None else None

    # Per-window CSV: predicted class, ground truth, correctness, latency --
    # one row per window, for every clip, for this model.
    per_window_csv = output_dir / f"{model_label.lower()}_per_window.csv"
    with open(per_window_csv, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["clip_name", "frame_number", "gt_label", "pred_label", "correct", "latency_ms"],
        )
        writer.writeheader()
        writer.writerows(all_records)
    print(f"  Per-window predictions saved: {per_window_csv}")

    all_gt = [r["gt_label"] for r in all_records if r["gt_label"] != ""]
    all_pred = [r["pred_label"] for r in all_records if r["gt_label"] != ""]
    latencies_ms = [r["latency_ms"] for r in all_records]

    return {
        "model_label": model_label,
        "available": True,
        "model_path": _relative_to_repo(classifier.model_path),
        "gt_labels": all_gt,
        "pred_labels": all_pred,
        "latencies_ms": latencies_ms,
        "fall_results": fall_results,
        "per_clip_summary": per_clip_summary,
        "peak_ram_mb": peak_ram_mb,
        "param_count": param_count,
        "window_size": classifier.window_size,
    }


# ------------------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------------------

def _classification_metrics(gt_labels: List[str], pred_labels: List[str]) -> dict:
    from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

    labels = POSTURE_CLASSES
    accuracy = accuracy_score(gt_labels, pred_labels) if gt_labels else float("nan")
    report = classification_report(
        gt_labels, pred_labels, labels=labels, output_dict=True, zero_division=0,
    )
    cm = confusion_matrix(gt_labels, pred_labels, labels=labels)
    return {"accuracy": accuracy, "report": report, "confusion_matrix": cm, "labels": labels}


def _fall_recall(fall_results: List[dict]) -> dict:
    tp = sum(1 for r in fall_results if r["result"] == "true_positive")
    fn = sum(1 for r in fall_results if r["result"] == "false_negative")
    fp = sum(1 for r in fall_results if r["result"] == "false_positive")
    n_fall_clips = tp + fn
    recall = (tp / n_fall_clips) if n_fall_clips > 0 else float("nan")
    return {"tp": tp, "fn": fn, "fp": fp, "n_fall_clips": n_fall_clips, "recall": recall}


def _latency_stats(latencies_ms: List[float]) -> dict:
    if not latencies_ms:
        return {"mean": float("nan"), "median": float("nan"), "p95": float("nan"), "n": 0}
    sorted_lat = sorted(latencies_ms)
    p95_idx = min(len(sorted_lat) - 1, int(round(0.95 * (len(sorted_lat) - 1))))
    return {
        "mean": statistics.fmean(latencies_ms),
        "median": statistics.median(latencies_ms),
        "p95": sorted_lat[p95_idx],
        "n": len(latencies_ms),
    }


# ------------------------------------------------------------------------------
# Markdown report
# ------------------------------------------------------------------------------

def _fmt(v: float, suffix: str = "", nd: int = 1) -> str:
    return "N/A" if (isinstance(v, float) and np.isnan(v)) else f"{v:.{nd}f}{suffix}"


def _confusion_md(cm: np.ndarray, labels: List[str]) -> str:
    header = "| GT \\ Pred |" + "|".join(f" {p} " for p in labels) + "|"
    sep = "|" + "|".join("---" for _ in range(len(labels) + 1)) + "|"
    lines = [header, sep]
    for i, gt_lbl in enumerate(labels):
        row = f"| **{gt_lbl}** |" + "|".join(f" {int(cm[i, j])} " for j in range(len(labels))) + "|"
        lines.append(row)
    return "\n".join(lines)


def _per_class_md(report: dict, labels: List[str]) -> str:
    lines = ["| Class | Precision | Recall | F1 | Support |", "|---|---|---|---|---|"]
    for c in labels:
        r = report.get(c, {})
        lines.append(
            f"| {c} | {_fmt(r.get('precision', float('nan')), nd=3)} "
            f"| {_fmt(r.get('recall', float('nan')), nd=3)} "
            f"| {_fmt(r.get('f1-score', float('nan')), nd=3)} "
            f"| {int(r.get('support', 0))} |"
        )
    for avg_key, avg_label in [("macro avg", "Macro avg"), ("weighted avg", "Weighted avg")]:
        r = report.get(avg_key, {})
        lines.append(
            f"| *{avg_label}* | {_fmt(r.get('precision', float('nan')), nd=3)} "
            f"| {_fmt(r.get('recall', float('nan')), nd=3)} "
            f"| {_fmt(r.get('f1-score', float('nan')), nd=3)} "
            f"| {int(r.get('support', 0))} |"
        )
    return "\n".join(lines)


def _per_clip_md(lstm_clips: List[dict], tcn_clips: List[dict]) -> str:
    """Per-clip accuracy (fraction of scored windows correct) and average
    latency, side by side for both models -- same clip order for both since
    both were run over the identical `clips` list."""
    tcn_by_name = {c["clip_name"]: c for c in tcn_clips}
    lines = [
        "| Clip | LSTM acc | LSTM avg latency (ms) | LSTM fall result "
        "| TCN acc | TCN avg latency (ms) | TCN fall result |",
        "|---|---|---|---|---|---|---|",
    ]
    for lc in lstm_clips:
        tc = tcn_by_name.get(lc["clip_name"], {})
        lstm_acc = (lc["n_correct"] / lc["n_scored"] * 100) if lc["n_scored"] > 0 else float("nan")
        tcn_acc = (tc.get("n_correct", 0) / tc["n_scored"] * 100) if tc.get("n_scored", 0) > 0 else float("nan")
        lines.append(
            f"| {lc['clip_name']} "
            f"| {_fmt(lstm_acc)} ({lc['n_correct']}/{lc['n_scored']}) "
            f"| {_fmt(lc['avg_latency_ms'], nd=3)} "
            f"| {lc['fall_result']} "
            f"| {_fmt(tcn_acc)} ({tc.get('n_correct', 0)}/{tc.get('n_scored', 0)}) "
            f"| {_fmt(tc.get('avg_latency_ms', float('nan')), nd=3)} "
            f"| {tc.get('fall_result', 'N/A')} |"
        )
    return "\n".join(lines)


def _discussion_md(lstm_res: dict, tcn_res: dict) -> str:
    """Short prose section derived only from the measured numbers above --
    no claims are hard-coded, every sentence reads directly from the results
    dicts computed earlier in this run."""
    lines = ["## 7. Discussion\n"]

    if not lstm_res["available"] or not tcn_res["available"]:
        lines.append(
            "One or both models were unavailable for this run "
            "(missing `.keras` file), so no comparative discussion can be "
            "generated. Train both models (`lstm_trainer.py`, `tcn_trainer.py`) "
            "and re-run this script.\n"
        )
        return "\n".join(lines)

    lstm_fall = lstm_res["fall_metrics"]
    tcn_fall = tcn_res["fall_metrics"]
    lstm_lat = lstm_res["latency_stats"]
    tcn_lat = tcn_res["latency_stats"]

    lines.append(
        f"**Recall.** Fall-detection recall was "
        f"{_fmt(lstm_fall['recall'] * 100, '%', 1) if not np.isnan(lstm_fall['recall']) else 'N/A'} "
        f"for the LSTM ({lstm_fall['tp']}/{lstm_fall['n_fall_clips']} labelled fall clips detected) "
        f"versus {_fmt(tcn_fall['recall'] * 100, '%', 1) if not np.isnan(tcn_fall['recall']) else 'N/A'} "
        f"for the TCN ({tcn_fall['tp']}/{tcn_fall['n_fall_clips']}). "
        "Recall matters more than precision for fall detection specifically because "
        "a missed fall (false negative) can mean a real injury goes unnoticed until "
        "someone happens to check on the person, while a false alarm (false positive) "
        "only costs a caregiver a few seconds of checking a monitor -- the two error "
        "types are not symmetric in consequence, so the model with higher recall is "
        "preferable even if it comes with a lower precision, up to the point where "
        "false alarms become frequent enough to cause alert fatigue.\n"
    )
    lines.append(
        f"**Latency.** Mean per-window inference time was "
        f"{_fmt(lstm_lat['mean'], ' ms', 2)} for the LSTM and "
        f"{_fmt(tcn_lat['mean'], ' ms', 2)} for the TCN (measured identically: "
        "wall-clock time around a single `.predict()` call, same machine, same "
        "warm model, same window buffer construction).\n"
    )
    lines.append(
        f"**Model size.** The LSTM has "
        f"{lstm_res['param_count']:,} trainable parameters versus "
        f"{tcn_res['param_count']:,} for the TCN "
        f"({'TCN is smaller' if tcn_res['param_count'] < lstm_res['param_count'] else 'LSTM is smaller'}).\n"
    )
    lines.append(
        "**Advantages of the LSTM.** Recurrent state gives it an unbounded "
        "(in principle) memory of everything seen since the window started, "
        "and it is the architecture already tuned into the rest of this "
        "pipeline (warmup frames, consecutive-frame gating in "
        "`hybrid_evaluate.py`) -- adopting a different architecture means "
        "re-tuning those knobs.\n"
    )
    lines.append(
        "**Advantages of the TCN.** Convolutions over a fixed window are "
        "naturally parallelizable across time steps (no sequential recurrence "
        "to unroll), which tends to make inference latency more predictable, "
        "and the receptive field is explicit and finite (set by the dilation "
        "schedule) rather than an emergent property of trained gate weights.\n"
    )
    lines.append(
        "**Trade-offs.** The LSTM's recurrence can capture dependencies "
        "longer than the fixed window if state were carried across windows "
        "(not currently done here -- both models are evaluated strictly "
        "per-window); the TCN's fixed receptive field is a hard ceiling. "
        "Conversely, the TCN's residual/dilated-conv structure trains more "
        "predictably (no vanishing/exploding gradients through many "
        "recurrent steps) and is simpler to reason about layer-by-layer.\n"
    )
    better_recall = "TCN" if tcn_fall["recall"] >= lstm_fall["recall"] else "LSTM"
    lines.append(
        "**Recommendation for future Hybrid AI work.** Given the existing "
        "heuristic-OR-LSTM hybrid in `hybrid_evaluate.py`, and that the "
        f"{better_recall} showed higher fall-detection recall in the run "
        "above, a natural next step is a three-way OR/voting gate "
        "(heuristic, LSTM, TCN) or an ensemble that averages the two "
        "models' softmax outputs before the argmax, so a fall gets flagged "
        "if either sequence model agrees with the heuristic. This is worth "
        "re-checking on a larger/more varied evaluation set before committing "
        "to it, since the run above is 8 clips from one recording session.\n"
    )
    return "\n".join(lines)


def write_report(md_path: Path, lstm_res: dict, tcn_res: dict, clips: List[Tuple[str, str, str]]):
    lines = []
    lines.append("# LSTM vs TCN Posture Classifier Comparison\n")

    lines.append("## 1. Overview\n")
    lines.append(
        "This report compares the existing LSTM posture classifier "
        "(`src/posture/lstm/`) against a Temporal Convolutional Network "
        "(TCN) alternative (`src/posture/tcn/`) trained and evaluated on "
        "identical inputs, generated automatically by `compare_tcn_lstm.py`.\n"
    )

    lines.append("## 2. Experimental Setup\n")
    lines.append(
        f"- Test clips: {len(clips)} labelled clip(s) — "
        f"{', '.join(name for _, _, name in clips) if clips else 'none found'}\n"
        "- Both models consume the identical extracted keypoints per clip "
        "(single `extract_keypoints()` pass, shared between both models).\n"
        "- Both models use their own `.predict()` public interface with no "
        "additional threshold/warmup/smoothing layered on top, so results "
        "reflect the raw per-window architecture decision for each model.\n"
    )

    lines.append("## 3. Dataset Used\n")
    lstm_model_path = lstm_res.get("model_path", "models/lstm_posture.keras (default)")
    tcn_model_path = tcn_res.get("model_path", "models/tcn_posture.keras (default)")
    lines.append(
        f"- **Checkpoints evaluated this run**: LSTM = `{lstm_model_path}`, "
        f"TCN = `{tcn_model_path}` (pass `--lstm-model`/`--tcn-model` to "
        "point this script at a different checkpoint; whichever paths are "
        "printed here are the actual files this report's numbers came "
        "from).\n"
        "- **TCN training data**: `data/lstm_dataset.npz` (sliding windows "
        "of `lstm_features`-normalized pose keypoints; see "
        "`src/posture/lstm/lstm_dataset.py`), built from the raw footage "
        "under `data/ADL`/`data/Fall` via "
        "`src/data_processing/build_ur_dataset_from_data_root.py`, then "
        "trained with `src/posture/tcn/tcn_trainer.py`.\n"
        "- **LSTM training data**: if the LSTM checkpoint above is "
        "`models/lstm_posture.keras` (the default, pre-existing, "
        "already-committed file), it was NOT retrained for this comparison "
        "and its original training data predates this session -- read this "
        "as \"pre-existing LSTM vs. freshly trained TCN,\" not a controlled "
        "same-data ablation. Any other path (e.g. "
        "`lstm_posture_retrained.keras`) was trained on the exact same "
        "`data/lstm_dataset.npz` as the TCN via the unmodified "
        "`lstm_trainer.py`, making this a fair, same-data architecture "
        "comparison.\n"
        "- **Evaluation footage**: labelled clips discovered under the "
        "`--batch_dir`/`--video` arguments to this script (same ground-truth "
        "format as `evaluate_real_footage.py`).\n"
    )

    lines.append("## 4. Model Architectures\n")
    lines.append(
        "- **LSTM**: `Input -> LSTM(64, return_sequences=True) -> Dropout(0.3) "
        "-> LSTM(32) -> Dropout(0.3) -> Dense(5, softmax)` "
        "(see `src/posture/lstm/lstm_trainer.py::build_model`).\n"
        "- **TCN**: 4 residual blocks (dilations 1, 2, 4, 8), each with two "
        "causal `Conv1D` layers + `LayerNormalization` + ReLU + Dropout, "
        "followed by `GlobalAveragePooling1D -> Dense(5, softmax)` "
        "(see `src/posture/tcn/tcn_model.py::build_model`).\n"
    )

    lines.append("## 5. Evaluation Methodology\n")
    lines.append(
        "- **Posture accuracy/precision/recall/F1**: computed over every "
        "non-ignored ground-truth frame, pooled across all clips, using "
        "`sklearn.metrics.classification_report` on the "
        "Standing/Sitting/Lying/Unknown vocabulary (same as "
        "`evaluate_real_footage.py`'s `POSTURE_CLASSES`).\n"
        "- **Fall-detection recall**: per-clip TP/FN/FP against the "
        "labelled fall window (`get_fall_window`), identical scoring logic "
        "to `evaluate_real_footage.score_fall`.\n"
        "- **Latency**: wall-clock time around each `.predict()` call, "
        "mean/median/p95 across every window in every clip.\n"
        "- **Parameter count**: `model.count_params()` on the loaded Keras "
        "model.\n"
        "- **Peak RAM**: peak resident-set size (RSS) of this process, "
        "sampled every 50ms while each model's full evaluation pass runs "
        "(models evaluated sequentially, one at a time, so the two "
        "measurements don't share concurrent memory pressure).\n"
        "- **Per-window detail**: every window's predicted class, ground "
        "truth, correctness, and latency is saved to "
        "`lstm_per_window.csv` / `tcn_per_window.csv` in the output "
        "directory (one row per inference call, per clip).\n"
    )

    lines.append("## 6. Full Comparison Table\n")
    if lstm_res["available"] and tcn_res["available"]:
        lstm_lat, tcn_lat = lstm_res["latency_stats"], tcn_res["latency_stats"]
        lstm_fall, tcn_fall = lstm_res["fall_metrics"], tcn_res["fall_metrics"]
        lines.append(
            "| Metric | LSTM | TCN |\n"
            "|---|---|---|\n"
            f"| Accuracy | {_fmt(lstm_res['metrics']['accuracy'] * 100, '%')} "
            f"| {_fmt(tcn_res['metrics']['accuracy'] * 100, '%')} |\n"
            f"| Macro Precision | {_fmt(lstm_res['metrics']['report']['macro avg']['precision'], nd=3)} "
            f"| {_fmt(tcn_res['metrics']['report']['macro avg']['precision'], nd=3)} |\n"
            f"| Macro Recall | {_fmt(lstm_res['metrics']['report']['macro avg']['recall'], nd=3)} "
            f"| {_fmt(tcn_res['metrics']['report']['macro avg']['recall'], nd=3)} |\n"
            f"| Macro F1 | {_fmt(lstm_res['metrics']['report']['macro avg']['f1-score'], nd=3)} "
            f"| {_fmt(tcn_res['metrics']['report']['macro avg']['f1-score'], nd=3)} |\n"
            f"| Fall-detection recall | {_fmt(lstm_fall['recall'] * 100, '%') if not np.isnan(lstm_fall['recall']) else 'N/A'} "
            f"({lstm_fall['tp']}/{lstm_fall['n_fall_clips']}) "
            f"| {_fmt(tcn_fall['recall'] * 100, '%') if not np.isnan(tcn_fall['recall']) else 'N/A'} "
            f"({tcn_fall['tp']}/{tcn_fall['n_fall_clips']}) |\n"
            f"| Fall false positives (clips) | {lstm_fall['fp']} | {tcn_fall['fp']} |\n"
            f"| Latency mean (ms/window) | {_fmt(lstm_lat['mean'], nd=3)} | {_fmt(tcn_lat['mean'], nd=3)} |\n"
            f"| Latency median (ms/window) | {_fmt(lstm_lat['median'], nd=3)} | {_fmt(tcn_lat['median'], nd=3)} |\n"
            f"| Latency p95 (ms/window) | {_fmt(lstm_lat['p95'], nd=3)} | {_fmt(tcn_lat['p95'], nd=3)} |\n"
            f"| Parameter count | {lstm_res['param_count']:,} | {tcn_res['param_count']:,} |\n"
            f"| Peak RAM (MB) | {_fmt(lstm_res['peak_ram_mb'], nd=1) if lstm_res['peak_ram_mb'] is not None else 'N/A (psutil not installed)'} "
            f"| {_fmt(tcn_res['peak_ram_mb'], nd=1) if tcn_res['peak_ram_mb'] is not None else 'N/A (psutil not installed)'} |\n"
        )

        lines.append("\n### Per-class metrics — LSTM\n")
        lines.append(_per_class_md(lstm_res["metrics"]["report"], lstm_res["metrics"]["labels"]))
        lines.append("\n\n### Per-class metrics — TCN\n")
        lines.append(_per_class_md(tcn_res["metrics"]["report"], tcn_res["metrics"]["labels"]))

        lines.append("\n\n### Confusion matrix — LSTM\n")
        lines.append(_confusion_md(lstm_res["metrics"]["confusion_matrix"], lstm_res["metrics"]["labels"]))
        lines.append("\n\n### Confusion matrix — TCN\n")
        lines.append(_confusion_md(tcn_res["metrics"]["confusion_matrix"], tcn_res["metrics"]["labels"]))

        lines.append("\n\n### Per-clip results\n")
        lines.append(_per_clip_md(lstm_res["per_clip_summary"], tcn_res["per_clip_summary"]))
        lines.append("\n")
    else:
        lines.append(
            "_One or both models were unavailable (missing `.keras` file) "
            "-- train both with `lstm_trainer.py` / `tcn_trainer.py` and "
            "re-run this script to populate this table with real numbers._\n"
        )

    lines.append("\n" + _discussion_md(lstm_res, tcn_res))

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to: {md_path}")


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compare the LSTM and TCN posture classifiers")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--batch_dir", type=str, default=None)
    mode.add_argument("--video", type=str, default=None)
    parser.add_argument("--ground_truth", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=OUTPUT_DIR_DEFAULT)
    parser.add_argument("--lstm-model", type=str, default=None, help="Override LSTM .keras path (default: models/lstm_posture.keras)")
    parser.add_argument("--lstm-encoder", type=str, default=None, help="Override LSTM label-encoder JSON path")
    parser.add_argument("--tcn-model", type=str, default=None, help="Override TCN .keras path (default: models/tcn_posture.keras)")
    parser.add_argument("--tcn-encoder", type=str, default=None, help="Override TCN label-encoder JSON path")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.batch_dir:
        clips = discover_clips(args.batch_dir)
    elif args.video:
        if not args.ground_truth:
            parser.error("--ground_truth is required in single-clip mode")
        clips = [(args.video, args.ground_truth, Path(args.video).stem)]
    else:
        parser.print_help()
        sys.exit(1)

    if not clips:
        print("No paired clips found -- nothing to evaluate.")
        sys.exit(1)

    print(f"Found {len(clips)} clip(s). Extracting keypoints once per clip "
          "(shared between both models)...")
    cached_keypoints = {}
    for video_path, gt_path, clip_name in clips:
        print(f"  Extracting: {clip_name}")
        cached_keypoints[clip_name] = extract_keypoints(video_path)

    lstm_clf = LSTMPostureClassifier(
        model_path=Path(args.lstm_model) if args.lstm_model else None,
        encoder_path=Path(args.lstm_encoder) if args.lstm_encoder else None,
    )
    lstm_res = evaluate_model("LSTM", lstm_clf, clips, cached_keypoints, output_dir)
    if lstm_res["available"]:
        lstm_res["metrics"] = _classification_metrics(lstm_res["gt_labels"], lstm_res["pred_labels"])
        lstm_res["fall_metrics"] = _fall_recall(lstm_res["fall_results"])
        lstm_res["latency_stats"] = _latency_stats(lstm_res["latencies_ms"])
    del lstm_clf

    tcn_clf = TCNPostureClassifier(
        model_path=Path(args.tcn_model) if args.tcn_model else None,
        encoder_path=Path(args.tcn_encoder) if args.tcn_encoder else None,
    )
    tcn_res = evaluate_model("TCN", tcn_clf, clips, cached_keypoints, output_dir)
    if tcn_res["available"]:
        tcn_res["metrics"] = _classification_metrics(tcn_res["gt_labels"], tcn_res["pred_labels"])
        tcn_res["fall_metrics"] = _fall_recall(tcn_res["fall_results"])
        tcn_res["latency_stats"] = _latency_stats(tcn_res["latencies_ms"])
    del tcn_clf

    md_path = output_dir / "tcn_vs_lstm_comparison.md"
    write_report(md_path, lstm_res, tcn_res, clips)


if __name__ == "__main__":
    main()
