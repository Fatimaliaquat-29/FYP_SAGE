"""
benchmarks/hgb_realfootage_confirm.py
=======================================
Real-footage confirmation of HistGradientBoostingClassifier (hgb_default)
directly against the current production Random Forest, on the EXACT SAME
protocol already established by benchmarks/rf_methodology_realfootage_confirm.py:

  - Same production train/val split (fold 0 of the same StratifiedGroupKFold,
    random_state=42 -- reused via load_production_split(), imported directly,
    not reimplemented).
  - Same two real-footage corpora (CORPORA, imported directly).
  - Same feature pipeline: both candidates are loaded through
    src/posture/rf/rf_classifier.py's RFPostureClassifier UNMODIFIED --
    that class only ever calls generic sklearn predict_proba()/classes_ on
    whatever `self._model` is; it never assumes RandomForestClassifier
    specifically, so a joblib-dumped HistGradientBoostingClassifier loads
    and runs through it with zero code changes (the one RF-specific line,
    `self._model.n_jobs = 1`, is a harmless no-op attribute set on HGB,
    which has no n_jobs parameter to force).
  - Same evaluate_model()/compare_tcn_lstm.py scoring machinery, same
    fall TP/FN/FP scoring (evaluate_real_footage.score_fall's logic, clip-
    level granularity -- see _fall_recall's own established meaning
    project-wide, e.g. rf_methodology_realfootage_confirm.py).
  - NO temporal smoothing/hysteresis on either candidate
    (fall_confirm_frames left at RFPostureClassifier's default of 1) --
    the existing RF protocol doesn't use it either, so adding it here would
    stop being an apples-to-apples comparison.
  - NO PCA/dimensionality reduction (already ruled out in
    benchmarks/dimensionality_reduction_sweep.json/.md).

The ONLY difference between the two candidates is the classifier fit on
top of an otherwise identical pipeline.

Latency note: the per-window latency this script measures (via
compare_tcn_lstm.evaluate_model -> run_model_over_clip) times the classifier's
ENTIRE .predict() call, which for RFPostureClassifier includes raw-window
feature extraction (extract_raw_keypoints + lstm_features normalization/
velocity/imputation) AND the classifier's predict_proba() call together --
this is what real per-frame deployment actually pays (realtime_fall_detection.py
calls this same .predict() once per frame), NOT classifier-only latency.
Classifier-only latency (post-feature-engineering) was already separately
measured for both classifiers in benchmarks/dimensionality_reduction_sweep.json
(baseline_rf_no_reduction / baseline_hgb_no_reduction) -- that number is
reused, not recomputed, in this script's final report.

Usage:
    python benchmarks/hgb_realfootage_confirm.py
    python benchmarks/hgb_realfootage_confirm.py --limit-clips 2   # smoke test only
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

from rf_methodology_realfootage_confirm import load_production_split, train_and_save_candidate, CORPORA
from evaluate_real_footage import discover_clips, extract_keypoints
from compare_tcn_lstm import build_ground_truth_cache, evaluate_model, _classification_metrics, _fall_recall, _latency_stats
from src.posture.rf.rf_classifier import RFPostureClassifier
from src.posture.rf.rf_trainer import MIN_SAMPLES_LEAF, MAX_FEATURES

RESULTS_DIR = REPO_ROOT / "results" / "rf_vs_hgb_realfootage"


def make_candidates():
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    return {
        "rf_baseline (production)": lambda: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
            n_jobs=-1, random_state=42,
        ),
        "hgb_default": lambda: HistGradientBoostingClassifier(
            max_iter=200, learning_rate=0.1, max_depth=None, l2_regularization=0.0,
            early_stopping=True, validation_fraction=0.1, n_iter_no_change=10, random_state=42,
        ),
    }


def _p99(latencies_ms):
    if not latencies_ms:
        return float("nan")
    s = sorted(latencies_ms)
    idx = min(len(s) - 1, int(round(0.99 * (len(s) - 1))))
    return s[idx]


def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit-clips", type=int, default=None,
                         help="Smoke-test only: cap total clips evaluated (does not change methodology, just scope)")
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

    print("Extracting keypoints once per clip (shared between both candidates)...")
    cached_keypoints = {}
    for video_path, gt_path, clip_name in all_clips:
        print(f"  Extracting: {clip_name}")
        cached_keypoints[clip_name] = extract_keypoints(video_path)
    cached_gt = build_ground_truth_cache(all_clips, cached_keypoints)

    print("Building production train/val split (fold 0, same as rf_trainer.py)...")
    split_data = load_production_split()

    candidates = make_candidates()
    results = {}

    from sklearn.metrics import balanced_accuracy_score

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for name, make_model in candidates.items():
            print(f"\n{'='*70}\nCandidate: {name}\n{'='*70}")
            model_path, encoder_path, val_acc = train_and_save_candidate(name, make_model, split_data, tmp_dir)
            model_size_kb = model_path.stat().st_size / 1024.0
            print(f"  validation-split accuracy: {val_acc:.4f}  model size: {model_size_kb:.1f}KB")

            clf = RFPostureClassifier(model_path=model_path, encoder_path=encoder_path)

            per_corpus = {}
            pooled_gt, pooled_pred, pooled_lat = [], [], []
            pooled_fall_results = []
            all_per_clip = []
            peak_ram_values = []

            for corpus_name, corpus_dir in CORPORA.items():
                clips = [c for c in all_clips if corpus_of[c[2]] == corpus_name]
                if not clips:
                    continue
                res = evaluate_model(f"{name} [{corpus_name}]", clf, clips, cached_keypoints, cached_gt, RESULTS_DIR)
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
                    "n_clips": len(clips),
                    "accuracy": metrics["accuracy"],
                    "balanced_accuracy": bal_acc,
                    "macro_f1": metrics["report"]["macro avg"]["f1-score"],
                    "macro_precision": metrics["report"]["macro avg"]["precision"],
                    "macro_recall": metrics["report"]["macro avg"]["recall"],
                    "weighted_f1": metrics["report"]["weighted avg"]["f1-score"],
                    "per_class": {c: metrics["report"].get(c, {}) for c in metrics["labels"]},
                    "confusion_matrix": metrics["confusion_matrix"].tolist(),
                    "confusion_labels": metrics["labels"],
                    "fall_tp": fall_metrics["tp"], "fall_fn": fall_metrics["fn"], "fall_fp": fall_metrics["fp"],
                    "fall_n_fall_clips": fall_metrics["n_fall_clips"], "fall_n_non_fall_clips": n_non_fall_clips,
                    "fall_recall": fall_metrics["recall"], "fall_precision": fall_precision, "fall_f1": fall_f1,
                    "fall_false_positive_rate": fall_fp_rate,
                    "latency_ms": lat,
                    "peak_ram_mb": res["peak_ram_mb"],
                    "per_clip_summary": res["per_clip_summary"],
                }
                pooled_gt.extend(res["gt_labels"]); pooled_pred.extend(res["pred_labels"])
                pooled_lat.extend(res["latencies_ms"]); pooled_fall_results.extend(res["fall_results"])
                all_per_clip.extend([{**c, "corpus": corpus_name} for c in res["per_clip_summary"]])
                if res["peak_ram_mb"] is not None:
                    peak_ram_values.append(res["peak_ram_mb"])
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

            results[name] = {
                "val_acc_cv_split": val_acc,
                "model_size_kb": model_size_kb,
                "per_corpus": per_corpus,
                "pooled": {
                    "n_clips": len(all_clips),
                    "accuracy": pooled_metrics["accuracy"], "balanced_accuracy": pooled_bal_acc,
                    "macro_f1": pooled_metrics["report"]["macro avg"]["f1-score"],
                    "weighted_f1": pooled_metrics["report"]["weighted avg"]["f1-score"],
                    "macro_precision": pooled_metrics["report"]["macro avg"]["precision"],
                    "macro_recall": pooled_metrics["report"]["macro avg"]["recall"],
                    "per_class": {c: pooled_metrics["report"].get(c, {}) for c in pooled_metrics["labels"]},
                    "confusion_matrix": pooled_metrics["confusion_matrix"].tolist(),
                    "confusion_labels": pooled_metrics["labels"],
                    "fall_tp": pooled_fall["tp"], "fall_fn": pooled_fall["fn"], "fall_fp": pooled_fall["fp"],
                    "fall_n_fall_clips": pooled_fall["n_fall_clips"], "fall_n_non_fall_clips": n_non_fall_total,
                    "fall_recall": pooled_fall["recall"], "fall_precision": pooled_precision, "fall_f1": pooled_f1,
                    "fall_false_positive_rate": pooled_fp_rate,
                    "latency_ms": pooled_lat_stats,
                    "peak_ram_mb_max": max(peak_ram_values) if peak_ram_values else None,
                },
                "per_clip": all_per_clip,
            }

    out_json = RESULTS_DIR / "summary.json"
    out_json.write_text(json.dumps(results, indent=2, default=_json_default), encoding="utf-8")
    print(f"\nFull results written -> {out_json}")

    # ── Failure-mode diff: per-clip join between the two candidates ────────
    names = list(candidates.keys())
    clips_a = {c["clip_name"]: c for c in results[names[0]]["per_clip"]}
    clips_b = {c["clip_name"]: c for c in results[names[1]]["per_clip"]}
    diffs = []
    for clip_name, a in clips_a.items():
        b = clips_b.get(clip_name, {})
        a_acc = (a["n_correct"] / a["n_scored"] * 100) if a["n_scored"] else float("nan")
        b_acc = (b.get("n_correct", 0) / b["n_scored"] * 100) if b.get("n_scored") else float("nan")
        acc_diff = abs(a_acc - b_acc) if not (np.isnan(a_acc) or np.isnan(b_acc)) else float("nan")
        fall_diff = a["fall_result"] != b.get("fall_result")
        diffs.append({
            "clip_name": clip_name, "corpus": a["corpus"],
            f"{names[0]}_acc": a_acc, f"{names[1]}_acc": b_acc, "acc_diff": acc_diff,
            f"{names[0]}_fall": a["fall_result"], f"{names[1]}_fall": b.get("fall_result"),
            "fall_result_differs": fall_diff,
        })
    diffs.sort(key=lambda d: (not d["fall_result_differs"], -(d["acc_diff"] if not np.isnan(d["acc_diff"]) else 0)))
    diffs_path = RESULTS_DIR / "per_clip_diff.json"
    diffs_path.write_text(json.dumps(diffs, indent=2, default=_json_default), encoding="utf-8")
    print(f"Per-clip RF-vs-HGB diff written -> {diffs_path}")

    print("\n\n" + "=" * 100 + "\nREAL-FOOTAGE CONFIRMATION SUMMARY (pooled, both corpora)\n" + "=" * 100)
    for name, r in results.items():
        p = r["pooled"]
        print(f"\n{name} (cv_val_acc={r['val_acc_cv_split']:.4f}, size={r['model_size_kb']:.1f}KB)")
        print(f"  accuracy={p['accuracy']*100:.1f}%  balanced_acc={p['balanced_accuracy']*100:.1f}%  "
              f"macro_f1={p['macro_f1']:.3f}  weighted_f1={p['weighted_f1']:.3f}")
        print(f"  fall: tp={p['fall_tp']} fn={p['fall_fn']} fp={p['fall_fp']} "
              f"recall={p['fall_recall']*100:.1f}%  precision={p['fall_precision']*100:.1f}%  "
              f"fp_rate={p['fall_false_positive_rate']*100:.1f}%")
        print(f"  latency (full pipeline, ms): mean={p['latency_ms']['mean']:.2f} "
              f"median={p['latency_ms']['median']:.2f} p95={p['latency_ms']['p95']:.2f} p99={p['latency_ms']['p99']:.2f}")
        print(f"  peak RAM: {p['peak_ram_mb_max']:.1f}MB" if p['peak_ram_mb_max'] is not None else "  peak RAM: N/A")

    print(f"\nTop clip-level RF/HGB divergences:")
    for d in diffs[:10]:
        print(f"  {d['clip_name']:<35} [{d['corpus']}]  acc_diff={d['acc_diff']:.1f}  "
              f"{names[0]}={d[f'{names[0]}_fall']:<16} {names[1]}={d[f'{names[1]}_fall']:<16} "
              f"{'<-- FALL RESULT DIFFERS' if d['fall_result_differs'] else ''}")


if __name__ == "__main__":
    main()
