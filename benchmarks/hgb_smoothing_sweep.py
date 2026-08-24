"""
benchmarks/hgb_smoothing_sweep.py
===================================
Re-runs the RF vs HGB real-footage confirmation (benchmarks/hgb_realfootage_confirm.py)
at each of several posture-smoothing window sizes, to test whether rolling
majority-vote smoothing (see src/posture/rf/rf_classifier.py::RFPostureClassifier._smooth,
a new, separate mechanism from the existing fall_confirm_frames -- that one
only gates the fall_detected BOOLEAN via consecutive-Fall counting and never
touches posture_label at all, so it does not generalize to this) changes
either candidate's real-footage behavior, and specifically whether it fixes
or reduces the SitFloor_crossedLegs failure mode found in the unsmoothed
confirmation run (HGB misread ~165/259 windows as Lying at 0.85-0.96
confidence -- sustained and high-confidence, not a brief flicker, so
majority-vote smoothing is NOT expected to fix it; tested empirically here
rather than assumed).

Protocol is UNCHANGED from hgb_realfootage_confirm.py except for the one
new axis: same load_production_split/train_and_save_candidate (both models
trained ONCE, reused across every smoothing window -- smoothing only
changes inference-time behavior, not what gets fit), same CORPORA/28
clips, same compare_tcn_lstm.evaluate_model/_classification_metrics/
_fall_recall/_latency_stats scoring, same clip-level fall TP/FN/FP
granularity, no PCA. fall_confirm_frames is left at its default (1,
disabled) throughout -- only smoothing_window is swept.

Usage:
    python benchmarks/hgb_smoothing_sweep.py
    python benchmarks/hgb_smoothing_sweep.py --limit-clips 2   # smoke test only
"""
import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BENCHMARKS_DIR = REPO_ROOT / "benchmarks"
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

from hgb_realfootage_confirm import make_candidates, _p99, _json_default
from rf_methodology_realfootage_confirm import load_production_split, train_and_save_candidate, CORPORA
from evaluate_real_footage import discover_clips, extract_keypoints
from compare_tcn_lstm import build_ground_truth_cache, evaluate_model, _classification_metrics, _fall_recall, _latency_stats
from src.posture.rf.rf_classifier import RFPostureClassifier

RESULTS_DIR = REPO_ROOT / "results" / "rf_vs_hgb_smoothing_sweep"
SMOOTHING_WINDOWS = [1, 3, 5, 7, 10]
WATCH_CLIP = "SitFloor_crossedLegs"


def evaluate_one(name, model_path, encoder_path, window, all_clips, corpus_of, cached_keypoints, cached_gt):
    from sklearn.metrics import balanced_accuracy_score

    label = f"{name} [smooth={window}]"
    clf = RFPostureClassifier(model_path=model_path, encoder_path=encoder_path, smoothing_window=window)

    per_corpus = {}
    pooled_gt, pooled_pred, pooled_lat = [], [], []
    pooled_fall_results = []
    watch_clip_summary = None

    for corpus_name, corpus_dir in CORPORA.items():
        clips = [c for c in all_clips if corpus_of[c[2]] == corpus_name]
        if not clips:
            continue
        res = evaluate_model(f"{label} [{corpus_name}]", clf, clips, cached_keypoints, cached_gt, RESULTS_DIR)
        if not res["available"]:
            per_corpus[corpus_name] = {"error": "model unavailable"}
            continue

        metrics = _classification_metrics(res["gt_labels"], res["pred_labels"])
        bal_acc = balanced_accuracy_score(res["gt_labels"], res["pred_labels"]) if res["gt_labels"] else float("nan")
        fall_metrics = _fall_recall(res["fall_results"])
        n_non_fall_clips = len(clips) - fall_metrics["n_fall_clips"]
        fall_fp_rate = (fall_metrics["fp"] / n_non_fall_clips) if n_non_fall_clips > 0 else float("nan")
        denom = fall_metrics["tp"] + fall_metrics["fp"]
        fall_precision = (fall_metrics["tp"] / denom) if denom > 0 else float("nan")
        fall_f1 = (2 * fall_precision * fall_metrics["recall"] / (fall_precision + fall_metrics["recall"])) \
            if (not np.isnan(fall_precision) and not np.isnan(fall_metrics["recall"])
                and (fall_precision + fall_metrics["recall"]) > 0) else float("nan")
        lat = _latency_stats(res["latencies_ms"])
        lat["p99"] = _p99(res["latencies_ms"])

        per_corpus[corpus_name] = {
            "n_clips": len(clips), "accuracy": metrics["accuracy"], "balanced_accuracy": bal_acc,
            "macro_f1": metrics["report"]["macro avg"]["f1-score"],
            "weighted_f1": metrics["report"]["weighted avg"]["f1-score"],
            "per_class": {c: metrics["report"].get(c, {}) for c in metrics["labels"]},
            "confusion_matrix": metrics["confusion_matrix"].tolist(), "confusion_labels": metrics["labels"],
            "fall_tp": fall_metrics["tp"], "fall_fn": fall_metrics["fn"], "fall_fp": fall_metrics["fp"],
            "fall_n_fall_clips": fall_metrics["n_fall_clips"], "fall_n_non_fall_clips": n_non_fall_clips,
            "fall_recall": fall_metrics["recall"], "fall_precision": fall_precision, "fall_f1": fall_f1,
            "fall_false_positive_rate": fall_fp_rate, "latency_ms": lat, "peak_ram_mb": res["peak_ram_mb"],
        }
        pooled_gt.extend(res["gt_labels"]); pooled_pred.extend(res["pred_labels"])
        pooled_lat.extend(res["latencies_ms"]); pooled_fall_results.extend(res["fall_results"])

        for c in res["per_clip_summary"]:
            if c["clip_name"] == WATCH_CLIP:
                watch_clip_summary = {**c, "corpus": corpus_name}
        clf.reset_state()

    pooled_metrics = _classification_metrics(pooled_gt, pooled_pred)
    pooled_bal_acc = balanced_accuracy_score(pooled_gt, pooled_pred) if pooled_gt else float("nan")
    pooled_fall = _fall_recall(pooled_fall_results)
    n_non_fall_total = len(all_clips) - pooled_fall["n_fall_clips"]
    pooled_fp_rate = (pooled_fall["fp"] / n_non_fall_total) if n_non_fall_total > 0 else float("nan")
    pdenom = pooled_fall["tp"] + pooled_fall["fp"]
    pooled_precision = (pooled_fall["tp"] / pdenom) if pdenom > 0 else float("nan")
    pooled_f1 = (2 * pooled_precision * pooled_fall["recall"] / (pooled_precision + pooled_fall["recall"])) \
        if (not np.isnan(pooled_precision) and not np.isnan(pooled_fall["recall"])
            and (pooled_precision + pooled_fall["recall"]) > 0) else float("nan")
    pooled_lat_stats = _latency_stats(pooled_lat)
    pooled_lat_stats["p99"] = _p99(pooled_lat)
    missed_falls = [r["clip_name"] for r in pooled_fall_results if r["result"] == "false_negative"]
    fp_clips = [r["clip_name"] for r in pooled_fall_results if r["result"] == "false_positive"]

    return {
        "smoothing_window": window,
        "per_corpus": per_corpus,
        "pooled": {
            "n_clips": len(all_clips), "accuracy": pooled_metrics["accuracy"], "balanced_accuracy": pooled_bal_acc,
            "macro_f1": pooled_metrics["report"]["macro avg"]["f1-score"],
            "weighted_f1": pooled_metrics["report"]["weighted avg"]["f1-score"],
            "per_class": {c: pooled_metrics["report"].get(c, {}) for c in pooled_metrics["labels"]},
            "confusion_matrix": pooled_metrics["confusion_matrix"].tolist(), "confusion_labels": pooled_metrics["labels"],
            "fall_tp": pooled_fall["tp"], "fall_fn": pooled_fall["fn"], "fall_fp": pooled_fall["fp"],
            "fall_n_fall_clips": pooled_fall["n_fall_clips"], "fall_n_non_fall_clips": n_non_fall_total,
            "fall_recall": pooled_fall["recall"], "fall_precision": pooled_precision, "fall_f1": pooled_f1,
            "fall_false_positive_rate": pooled_fp_rate, "latency_ms": pooled_lat_stats,
            "missed_fall_clips": missed_falls, "false_positive_clips": fp_clips,
        },
        "watch_clip": watch_clip_summary,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit-clips", type=int, default=None)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Discovering real-footage clips (both corpora)...")
    all_clips = []
    corpus_of = {}
    for corpus_name, corpus_dir in CORPORA.items():
        clips = discover_clips(str(corpus_dir))
        all_clips.extend(clips)
        for _, _, clip_name in clips:
            corpus_of[clip_name] = corpus_name
    if args.limit_clips:
        all_clips = all_clips[:args.limit_clips]
        corpus_of = {c[2]: corpus_of[c[2]] for c in all_clips}
    print(f"  {len(all_clips)} clips total: " +
          ", ".join(f"{k}={sum(1 for c in corpus_of.values() if c == k)}" for k in CORPORA))

    print("Extracting keypoints once per clip (shared across every model x window combo)...")
    cached_keypoints = {}
    fps_by_clip = {}
    for video_path, gt_path, clip_name in all_clips:
        print(f"  Extracting: {clip_name}")
        kp_rows, fps, total_frames = extract_keypoints(video_path)
        cached_keypoints[clip_name] = (kp_rows, fps, total_frames)
        fps_by_clip[clip_name] = fps
    cached_gt = build_ground_truth_cache(all_clips, cached_keypoints)
    mean_fps = float(np.mean(list(fps_by_clip.values())))
    print(f"  Mean clip fps: {mean_fps:.2f} (range {min(fps_by_clip.values()):.2f}-{max(fps_by_clip.values()):.2f})")

    print("Building production train/val split (fold 0, same as rf_trainer.py)...")
    split_data = load_production_split()

    candidates = make_candidates()
    results = {}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        model_paths = {}
        for name, make_model in candidates.items():
            print(f"\n{'='*70}\nTraining candidate (once): {name}\n{'='*70}")
            model_path, encoder_path, val_acc = train_and_save_candidate(name, make_model, split_data, tmp_dir)
            model_paths[name] = (model_path, encoder_path)
            print(f"  validation-split accuracy: {val_acc:.4f}")

        for name, (model_path, encoder_path) in model_paths.items():
            results[name] = {}
            for window in SMOOTHING_WINDOWS:
                print(f"\n{'='*70}\n{name} @ smoothing_window={window}\n{'='*70}")
                results[name][str(window)] = evaluate_one(
                    name, model_path, encoder_path, window, all_clips, corpus_of, cached_keypoints, cached_gt)

    out_json = RESULTS_DIR / "summary.json"
    out_json.write_text(json.dumps({
        "mean_fps": mean_fps, "fps_by_clip": fps_by_clip, "smoothing_windows": SMOOTHING_WINDOWS,
        "watch_clip": WATCH_CLIP, "results": results,
    }, indent=2, default=_json_default), encoding="utf-8")
    print(f"\nFull results written -> {out_json}")

    print("\n\n" + "=" * 100 + f"\nSMOOTHING SWEEP SUMMARY (pooled, both corpora, {len(all_clips)} clips)\n" + "=" * 100)
    for name in results:
        for window in SMOOTHING_WINDOWS:
            r = results[name][str(window)]
            p = r["pooled"]
            delay_ms = (window - 1) / mean_fps * 1000.0
            wc = r["watch_clip"]
            wc_str = f"{WATCH_CLIP}: {wc['fall_result']} ({wc['n_correct']}/{wc['n_scored']} acc)" if wc else "N/A"
            print(f"\n{name} @ N={window} (added delay ~{delay_ms:.0f}ms @ {mean_fps:.1f}fps)")
            print(f"  acc={p['accuracy']*100:.1f}% bal_acc={p['balanced_accuracy']*100:.1f}% "
                  f"macro_f1={p['macro_f1']:.3f} weighted_f1={p['weighted_f1']:.3f}")
            print(f"  fall: tp={p['fall_tp']} fn={p['fall_fn']} fp={p['fall_fp']} recall={p['fall_recall']*100:.1f}% "
                  f"fp_rate={p['fall_false_positive_rate']*100:.1f}%  missed={p['missed_fall_clips']}")
            print(f"  {WATCH_CLIP}: {wc_str}")


if __name__ == "__main__":
    main()
