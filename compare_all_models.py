"""
compare_all_models.py
======================
Three-way extension of compare_tcn_lstm.py: evaluates LSTM, TCN, and Random
Forest posture classifiers under IDENTICAL conditions on the same labelled
test footage (same extracted keypoints, same windowing, same raw per-window
decision with no smoothing/warmup layered on top -- see compare_tcn_lstm.py's
module docstring for the full rationale, which applies unchanged here).

Reuses compare_tcn_lstm.py's evaluation primitives (evaluate_model,
_classification_metrics, _fall_recall, _latency_stats, markdown helpers)
rather than duplicating them, and adds a Random Forest column throughout.

Usage
-----
  python compare_all_models.py --batch_dir "test_footage/Sanawar Testing 7-22-26" --output_dir results/all_models_sanawar
  python compare_all_models.py --batch_dir "test_footage/Hussain Testing 7-30-26" --output_dir results/all_models_hussain
"""

import argparse
import sys
from pathlib import Path
from typing import List

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evaluate_real_footage import discover_clips, extract_keypoints
from compare_tcn_lstm import (
    build_ground_truth_cache, evaluate_model, _classification_metrics,
    _fall_recall, _latency_stats, _confusion_md, _per_class_md, _fmt,
    _relative_to_repo,
)
from src.posture.lstm.lstm_classifier import LSTMPostureClassifier
from src.posture.tcn.tcn_classifier import TCNPostureClassifier
from src.posture.rf.rf_classifier import RFPostureClassifier

MODEL_ORDER = ["LSTM", "TCN", "RF"]
OUTPUT_DIR_DEFAULT = "results/all_models"


def _model_file_size_kb(path_str) -> float:
    p = Path(path_str)
    if not p.exists():
        return float("nan")
    return p.stat().st_size / 1024.0


def write_report(md_path: Path, results: dict, clips):
    lines = []
    lines.append("# LSTM vs TCN vs Random Forest Posture Classifier Comparison\n")
    lines.append(
        "Generated automatically by `compare_all_models.py`. All three models "
        "consume the identical extracted keypoints per clip and their own "
        "`.predict()` public interface with no additional threshold/warmup/"
        "smoothing layered on top, so results reflect each architecture's raw "
        "per-window decision.\n"
    )
    lines.append(f"Test clips: {len(clips)} — {', '.join(name for _, _, name in clips)}\n")

    lines.append("\n## Full Comparison Table\n")
    header = "| Metric | " + " | ".join(MODEL_ORDER) + " |\n"
    sep = "|---|" + "|".join("---" for _ in MODEL_ORDER) + "|\n"
    rows = []

    def row(label, fmt_fn):
        vals = [fmt_fn(results[m]) for m in MODEL_ORDER]
        return f"| {label} | " + " | ".join(vals) + " |\n"

    rows.append(row("Accuracy", lambda r: _fmt(r["metrics"]["accuracy"] * 100, "%") if r["available"] else "N/A"))
    rows.append(row("Macro Precision", lambda r: _fmt(r["metrics"]["report"]["macro avg"]["precision"], nd=3) if r["available"] else "N/A"))
    rows.append(row("Macro Recall", lambda r: _fmt(r["metrics"]["report"]["macro avg"]["recall"], nd=3) if r["available"] else "N/A"))
    rows.append(row("Macro F1", lambda r: _fmt(r["metrics"]["report"]["macro avg"]["f1-score"], nd=3) if r["available"] else "N/A"))
    rows.append(row("Fall-detection recall", lambda r: (f"{_fmt(r['fall_metrics']['recall']*100, '%')} ({r['fall_metrics']['tp']}/{r['fall_metrics']['n_fall_clips']})" if r["available"] and not np.isnan(r["fall_metrics"]["recall"]) else "N/A")))
    rows.append(row("Fall false positives (clips)", lambda r: str(r["fall_metrics"]["fp"]) if r["available"] else "N/A"))
    rows.append(row("Latency mean (ms/window)", lambda r: _fmt(r["latency_stats"]["mean"], nd=3) if r["available"] else "N/A"))
    rows.append(row("Latency p95 (ms/window)", lambda r: _fmt(r["latency_stats"]["p95"], nd=3) if r["available"] else "N/A"))
    rows.append(row("Parameter/node count", lambda r: f"{r['param_count']:,}" if r["available"] and r["param_count"] is not None else "N/A"))
    rows.append(row("Model file size (KB)", lambda r: _fmt(r["model_size_kb"], nd=1) if r["available"] else "N/A"))
    rows.append(row("Peak RAM (MB)", lambda r: _fmt(r["peak_ram_mb"], nd=1) if r["available"] and r["peak_ram_mb"] is not None else "N/A"))

    lines.append(header + sep + "".join(rows))

    for m in MODEL_ORDER:
        r = results[m]
        if not r["available"]:
            lines.append(f"\n_{m} unavailable this run._\n")
            continue
        lines.append(f"\n### Per-class metrics — {m}\n")
        lines.append(_per_class_md(r["metrics"]["report"], r["metrics"]["labels"]))
        lines.append(f"\n\n### Confusion matrix — {m}\n")
        lines.append(_confusion_md(r["metrics"]["confusion_matrix"], r["metrics"]["labels"]))
        lines.append("\n")

    lines.append("\n### Per-clip accuracy\n")
    header2 = "| Clip | " + " | ".join(f"{m} acc" for m in MODEL_ORDER) + " | " + " | ".join(f"{m} fall result" for m in MODEL_ORDER) + " |\n"
    sep2 = "|" + "|".join("---" for _ in range(1 + 2 * len(MODEL_ORDER))) + "|\n"
    body = []
    for i, (_, _, clip_name) in enumerate(clips):
        accs = []
        falls = []
        for m in MODEL_ORDER:
            r = results[m]
            if not r["available"]:
                accs.append("N/A"); falls.append("N/A")
                continue
            summary = next((s for s in r["per_clip_summary"] if s["clip_name"] == clip_name), None)
            if summary is None or summary["n_scored"] == 0:
                accs.append("N/A")
            else:
                accs.append(f"{summary['n_correct']/summary['n_scored']*100:.1f} ({summary['n_correct']}/{summary['n_scored']})")
            falls.append(summary["fall_result"] if summary else "N/A")
        body.append(f"| {clip_name} | " + " | ".join(accs) + " | " + " | ".join(falls) + " |\n")
    lines.append(header2 + sep2 + "".join(body))

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to: {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare LSTM, TCN, and Random Forest posture classifiers")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--batch_dir", type=str, default=None)
    mode.add_argument("--video", type=str, default=None)
    parser.add_argument("--ground_truth", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=OUTPUT_DIR_DEFAULT)
    parser.add_argument("--lstm-model", type=str, default=None)
    parser.add_argument("--lstm-encoder", type=str, default=None)
    parser.add_argument("--tcn-model", type=str, default=None)
    parser.add_argument("--tcn-encoder", type=str, default=None)
    parser.add_argument("--rf-model", type=str, default=None)
    parser.add_argument("--rf-encoder", type=str, default=None)
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

    print(f"Found {len(clips)} clip(s). Extracting keypoints once per clip (shared across all 3 models)...")
    cached_keypoints = {}
    for video_path, gt_path, clip_name in clips:
        print(f"  Extracting: {clip_name}")
        cached_keypoints[clip_name] = extract_keypoints(video_path)

    cached_gt = build_ground_truth_cache(clips, cached_keypoints)

    classifiers = {
        "LSTM": (
            LSTMPostureClassifier(
                model_path=Path(args.lstm_model) if args.lstm_model else None,
                encoder_path=Path(args.lstm_encoder) if args.lstm_encoder else None,
            )
        ),
        "TCN": (
            TCNPostureClassifier(
                model_path=Path(args.tcn_model) if args.tcn_model else None,
                encoder_path=Path(args.tcn_encoder) if args.tcn_encoder else None,
            )
        ),
        "RF": (
            RFPostureClassifier(
                model_path=Path(args.rf_model) if args.rf_model else None,
                encoder_path=Path(args.rf_encoder) if args.rf_encoder else None,
            )
        ),
    }

    results = {}
    for label in MODEL_ORDER:
        clf = classifiers[label]
        res = evaluate_model(label, clf, clips, cached_keypoints, cached_gt, output_dir)
        if res["available"]:
            res["metrics"] = _classification_metrics(res["gt_labels"], res["pred_labels"])
            res["fall_metrics"] = _fall_recall(res["fall_results"])
            res["latency_stats"] = _latency_stats(res["latencies_ms"])
            res["model_size_kb"] = _model_file_size_kb(clf.model_path)
        results[label] = res
        del clf

    md_path = output_dir / "all_models_comparison.md"
    write_report(md_path, results, clips)


if __name__ == "__main__":
    main()
