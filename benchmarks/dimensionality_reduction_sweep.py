"""
benchmarks/dimensionality_reduction_sweep.py
==============================================
Analysis-only comparison of dimensionality-reduction techniques for the
flattened 3,960-dim RF/GB feature space (docs/RF_GENERALIZATION_INVESTIGATION.md's
root-cause diagnosis: ~56 independent real training SEQUENCES vs 3,960
flattened features -- an extreme sample-to-feature ratio). This is
evidence-gathering only, NOT wired into any production trainer -- per
explicit instruction, this is an analyze-and-recommend step; nothing here
changes rf_trainer.py or models/rf_posture.joblib.

Reuses benchmarks/rf_alternatives_full_sweep.py's load_folds() (identical
5-fold StratifiedGroupKFold, grouped by sequence_id, train-fold-only
median imputation, post-split synthetic augmentation) and its
_metrics/_model_size_kb/_atomic_write_json/candidate_signature helpers
directly, rather than reimplementing them, so this script's leakage
guarantees can never silently drift from that one's.

Candidates evaluated with real CV (accuracy, macro F1, fit time,
transform-only latency, classify-only latency, combined latency, and
serialized pipeline size -- every metric requested, not just accuracy):
  - PCA(n=50/100/200) + RF -- re-confirms round 1's PCA+RF result
    (never persisted to disk -- see rf_alternatives_full_sweep.py's own
    docstring for the same problem with round 1's GB number) under this
    round's full instrumentation.
  - PCA(n=50/100/200) + HistGB -- tests whether round 1's PCA-hurts-RF
    result is RF-specific or a property of the flatten-space+PCA
    combination regardless of classifier.
  - FeatureAgglomeration(n=50/100/200) + RF / + HistGB -- Ward-linkage
    clustering of CORRELATED FEATURES (not samples), then averaging
    within each cluster. Picked as the "genuinely well-suited" third
    candidate: unlike PCA it doesn't require a dense global rotation
    matrix at inference time (transform is a per-cluster mean -- cheap,
    and each cluster only touches the raw features it was built from),
    and it doesn't assume one global linear-variance structure across a
    feature space that mixes positions and velocities from very
    different scales.
  - GaussianRandomProjection(n=50/100/200) + RF / + HistGB -- a
    near-free, data-agnostic floor (Johnson-Lindenstrauss): fits without
    even looking at label structure, near-instant transform, included as
    a sanity check on whether ANY dimensionality cut helps here at all,
    independent of whether the cut is "smart".
  - baseline_rf_no_reduction / baseline_hgb_no_reduction -- the
    un-reduced flatten-space classifiers, for reference (same configs as
    rf_alternatives_full_sweep.py's rf_baseline/hgb_default).

Candidates deliberately NOT run with CV (ruled out on architectural
grounds -- see printed report for the same reasoning, kept in sync here):
  - t-SNE: sklearn's TSNE has no .transform() for new points -- every
    embedding is refit from scratch on whatever data is in hand. Placing
    one new, unseen window from live footage into an existing embedding
    means either refitting on old+new data together (incompatible with
    single-window real-time inference) or bolting on an approximate
    out-of-sample method (e.g. a parametric neural net trained to mimic
    a fixed t-SNE embedding) -- a second model, trained on this same
    ~56-sequence-scarce dataset, just to approximate an embedding. Not a
    reasonable trade against t-SNE's nonlinear-structure upside here.
  - Kernel PCA: exact out-of-sample transform requires evaluating a
    kernel between the new point and (a stored subset of) the training
    set at inference time -- i.e. training data must be kept in memory
    and touched on every real-time prediction, a materially heavier and
    different inference-time dependency than every other candidate here
    (all of which reduce to one small, fixed, in-memory transform
    matrix). Ruled out on the same "fast inference-time transform on new
    sequences" constraint driving this whole analysis.

Usage:
    python benchmarks/dimensionality_reduction_sweep.py
    python benchmarks/dimensionality_reduction_sweep.py --fresh
    python benchmarks/dimensionality_reduction_sweep.py --folds 2   # quick read
"""
import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
BENCHMARKS_DIR = REPO_ROOT / "benchmarks"
if str(BENCHMARKS_DIR) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_DIR))

import rf_alternatives_full_sweep as base  # reuse load_folds/_metrics/_model_size_kb/_atomic_write_json/candidate_signature
from src.posture.rf.rf_trainer import MIN_SAMPLES_LEAF, MAX_FEATURES

RESULTS_DIR = REPO_ROOT / "benchmarks" / "results"
DEFAULT_N_FOLDS = 5
N_LATENCY_SAMPLES = 200


def make_candidates():
    from sklearn.decomposition import PCA
    from sklearn.cluster import FeatureAgglomeration
    from sklearn.random_projection import GaussianRandomProjection
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.pipeline import make_pipeline

    rf_cfg = dict(n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
                  n_jobs=-1, random_state=42)
    hgb_cfg = dict(max_iter=200, learning_rate=0.1, max_depth=None, l2_regularization=0.0,
                   early_stopping=True, validation_fraction=0.1, n_iter_no_change=10, random_state=42)

    reducers = {
        "pca": lambda k: PCA(n_components=k, random_state=42),
        "agglom": lambda k: FeatureAgglomeration(n_clusters=k),
        "randproj": lambda k: GaussianRandomProjection(n_components=k, random_state=42),
    }
    classifier_fns = {
        "rf": lambda: RandomForestClassifier(**rf_cfg),
        "hgb": lambda: HistGradientBoostingClassifier(**hgb_cfg),
    }
    classifier_cfg = {"rf": rf_cfg, "hgb": hgb_cfg}

    candidates = {}
    for reducer_name, reducer_fn in reducers.items():
        for k in (50, 100, 200):
            for clf_name, clf_fn in classifier_fns.items():
                name = f"{reducer_name}(n={k})+{clf_name}"
                cfg = {"reducer": reducer_name, "n_components": k, "classifier": clf_name,
                       **classifier_cfg[clf_name]}
                candidates[name] = (
                    clf_name,
                    cfg,
                    (lambda rfn=reducer_fn, kk=k, cf=clf_fn: make_pipeline(rfn(kk), cf())),
                )

    candidates["baseline_rf_no_reduction"] = ("rf", {"classifier": "rf", **rf_cfg},
                                               lambda: RandomForestClassifier(**rf_cfg))
    candidates["baseline_hgb_no_reduction"] = ("hgb", {"classifier": "hgb", **hgb_cfg},
                                                lambda: HistGradientBoostingClassifier(**hgb_cfg))
    return candidates


def _measure_pipeline_latency_ms(model, clf_name, X_val_flat, rng, n_samples=N_LATENCY_SAMPLES):
    """Times the reducer's transform() and the classifier's predict_proba()
    SEPARATELY, on single (1, n_features) rows -- matching real deployment
    (one new window per video frame, never a batch): the pipeline a
    reduced-dim model would actually ship as is raw-window -> transform()
    -> predict_proba(), and both stages matter for whether the reduction
    is worth its added pipeline complexity. For the two no-reduction
    baselines (plain classifiers, not sklearn Pipelines), transform time
    is definitionally 0.

    n_jobs is forced to 1 on RF classifier stages before timing, mirroring
    src/posture/rf/rf_classifier.py's own forced single-threaded inference
    (see rf_alternatives_full_sweep.py's identical comment for why)."""
    from sklearn.pipeline import Pipeline

    is_pipeline = isinstance(model, Pipeline)
    if clf_name == "rf":
        clf_step = model.steps[-1][1] if is_pipeline else model
        clf_step.n_jobs = 1

    n = min(n_samples, X_val_flat.shape[0])
    idx = rng.choice(X_val_flat.shape[0], size=n, replace=False)
    transform_ms, classify_ms, total_ms = [], [], []
    for i in idx:
        row = X_val_flat[i:i + 1]
        if is_pipeline:
            reducer = model[:-1]
            classifier = model.steps[-1][1]
            t0 = time.perf_counter()
            reduced = reducer.transform(row)
            t1 = time.perf_counter()
            classifier.predict_proba(reduced)
            t2 = time.perf_counter()
            transform_ms.append((t1 - t0) * 1000.0)
            classify_ms.append((t2 - t1) * 1000.0)
            total_ms.append((t2 - t0) * 1000.0)
        else:
            t0 = time.perf_counter()
            model.predict_proba(row)
            t1 = time.perf_counter()
            transform_ms.append(0.0)
            classify_ms.append((t1 - t0) * 1000.0)
            total_ms.append((t1 - t0) * 1000.0)
    return transform_ms, classify_ms, total_ms


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--folds", type=int, default=DEFAULT_N_FOLDS)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    n_folds = args.folds

    results_json = RESULTS_DIR / "dimensionality_reduction_sweep.json"
    results_md = RESULTS_DIR / "dimensionality_reduction_comparison.md"

    print(f"Loading dataset from {base.LSTM_DATASET_NPZ}...")
    candidates = make_candidates()
    sig = base.candidate_signature(candidates, n_folds, False)
    total_pairs = len(candidates) * n_folds

    raw = None
    started_at = None
    if not args.fresh and results_json.exists():
        try:
            existing = json.loads(results_json.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Existing {results_json.name} could not be parsed ({e}) -- starting fresh.")
            existing = None
        if existing is not None:
            if existing.get("candidate_signature") == sig and existing.get("status") == "in_progress":
                raw = existing["raw_per_fold"]
                started_at = existing["started_at"]
                done = sum(len(v["folds"]) for v in raw.values())
                print(f"Resuming in-progress run: {done}/{total_pairs} candidate-fold results already on disk.")
            else:
                print(f"Existing {results_json.name} not resumable for this config -- starting fresh.")

    if raw is None:
        raw = {name: {"family": family, "config": cfg, "folds": []} for name, (family, cfg, _fn) in candidates.items()}
        started_at = datetime.now(timezone.utc).isoformat()

    completed_pairs = {(name, f["fold"]) for name, rec in raw.items() for f in rec["folds"]}

    def save_in_progress():
        base._atomic_write_json(results_json, {
            "status": "in_progress", "candidate_signature": sig, "n_folds": n_folds,
            "n_latency_samples_per_fold": N_LATENCY_SAMPLES,
            "started_at": started_at, "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "raw_per_fold": raw,
        })

    save_in_progress()
    print(f"{len(candidates)} candidates x {n_folds} folds. {len(completed_pairs)}/{total_pairs} already complete.\n")

    rng = np.random.default_rng(seed=123)
    newly_fit_times = []
    for fold_i, X_train, y_train, X_val, y_val, classes in base.load_folds(n_folds):
        print(f"\n=== Fold {fold_i} (train={len(X_train)}, val={len(X_val)}) ===")
        for name, (family, cfg, make_model) in candidates.items():
            if (name, fold_i) in completed_pairs:
                print(f"  {name:<35} [skip -- already completed]")
                continue

            cand_t0 = time.perf_counter()
            t0 = time.perf_counter()
            model = make_model()
            model.fit(X_train, y_train)
            fit_time = time.perf_counter() - t0

            y_pred = model.predict(X_val)
            y_train_acc = model.score(X_train, y_train)
            m = base._metrics(y_val, y_pred, y_train_acc)

            transform_ms, classify_ms, total_ms = _measure_pipeline_latency_ms(model, family, X_val, rng)
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                size_kb = base._model_size_kb(model, Path(tmp))

            fold_record = {
                "fold": fold_i, **m, "fit_time_s": fit_time,
                "transform_latency_ms_mean": float(np.mean(transform_ms)),
                "transform_latency_ms_p95": float(np.percentile(transform_ms, 95)),
                "classify_latency_ms_mean": float(np.mean(classify_ms)),
                "classify_latency_ms_p95": float(np.percentile(classify_ms, 95)),
                "total_latency_ms_mean": float(np.mean(total_ms)),
                "total_latency_ms_p95": float(np.percentile(total_ms, 95)),
                "model_size_kb": size_kb,
            }
            raw[name]["folds"].append(fold_record)
            save_in_progress()
            newly_fit_times.append(time.perf_counter() - cand_t0)

            print(f"  {name:<35} val_acc={m['val_acc']:.4f} macro_f1={m['macro_f1']:.4f} "
                  f"fit={fit_time:6.1f}s  total_p95={fold_record['total_latency_ms_p95']:6.2f}ms  "
                  f"size={size_kb:8.1f}KB")

        done = sum(len(v["folds"]) for v in raw.values())
        remaining = total_pairs - done
        if newly_fit_times and remaining > 0:
            avg = sum(newly_fit_times) / len(newly_fit_times)
            eta_s = avg * remaining
            eta_finish = datetime.now().astimezone() + timedelta(seconds=eta_s)
            print(f"\n[ETA] {done}/{total_pairs} done. ~{eta_s/60:.1f}min remaining, "
                  f"estimated finish ~{eta_finish.strftime('%Y-%m-%d %H:%M')}.\n")

    # ── Aggregate ────────────────────────────────────────────────────────
    summary = {}
    for name, rec in raw.items():
        folds = rec["folds"]
        summary[name] = {
            "family": rec["family"], "config": rec["config"],
            "val_acc": float(np.mean([f["val_acc"] for f in folds])),
            "macro_f1": float(np.mean([f["macro_f1"] for f in folds])),
            "balanced_acc": float(np.mean([f["balanced_acc"] for f in folds])),
            "gap": float(np.mean([f["gap"] for f in folds])),
            "fit_time_s_mean": float(np.mean([f["fit_time_s"] for f in folds])),
            "transform_latency_ms_mean": float(np.mean([f["transform_latency_ms_mean"] for f in folds])),
            "transform_latency_ms_p95": float(np.mean([f["transform_latency_ms_p95"] for f in folds])),
            "classify_latency_ms_mean": float(np.mean([f["classify_latency_ms_mean"] for f in folds])),
            "classify_latency_ms_p95": float(np.mean([f["classify_latency_ms_p95"] for f in folds])),
            "total_latency_ms_mean": float(np.mean([f["total_latency_ms_mean"] for f in folds])),
            "total_latency_ms_p95": float(np.mean([f["total_latency_ms_p95"] for f in folds])),
            "model_size_kb_mean": float(np.mean([f["model_size_kb"] for f in folds])),
        }

    base._atomic_write_json(results_json, {
        "status": "complete", "candidate_signature": sig, "n_folds": n_folds,
        "n_latency_samples_per_fold": N_LATENCY_SAMPLES,
        "started_at": started_at, "completed_at": datetime.now(timezone.utc).isoformat(),
        "raw_per_fold": raw, "summary": summary,
    })
    print(f"\nFull per-fold results written -> {results_json}")

    # ── Comparison table ─────────────────────────────────────────────────
    rf_base = summary["baseline_rf_no_reduction"]
    hgb_base = summary["baseline_hgb_no_reduction"]
    lines = [f"# Dimensionality-reduction comparison ({n_folds}-fold)\n"]
    lines.append("StratifiedGroupKFold (grouped by sequence_id). Latency = single-row transform()/predict_proba(), "
                  "matching real per-frame inference. RF classifier stages timed with n_jobs forced to 1 "
                  "(matches production src/posture/rf/rf_classifier.py).\n")
    header = ("| Candidate | Accuracy | Macro F1 | Fit time (s) | Transform p95 (ms) | "
              "Classify p95 (ms) | Total p95 (ms) | Size (KB) |")
    lines.append(header)
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, s in summary.items():
        marker = " **(no-reduction baseline)**" if "no_reduction" in name else ""
        lines.append(f"| {name}{marker} | {s['val_acc']:.4f} | {s['macro_f1']:.4f} | {s['fit_time_s_mean']:.1f} | "
                      f"{s['transform_latency_ms_p95']:.3f} | {s['classify_latency_ms_p95']:.3f} | "
                      f"{s['total_latency_ms_p95']:.3f} | {s['model_size_kb_mean']:.1f} |")

    lines.append("\n## Ruled out without CV\n")
    lines.append("- **t-SNE**: no `.transform()` for new points -- every embedding is refit from scratch on "
                  "whatever data is in hand; placing one new real-time window requires either refitting on "
                  "old+new data (incompatible with single-window inference) or a second approximation model "
                  "trained on this same ~56-sequence-scarce dataset. Not run.")
    lines.append("- **Kernel PCA**: exact out-of-sample transform needs the training set (or a stored subset) "
                  "kept in memory and kernel-evaluated on every real-time prediction -- a heavier, different "
                  "inference-time dependency than every other candidate here. Not run.")

    lines.append("\n## Verdict\n")
    best = max(summary.items(), key=lambda kv: (kv[1]["val_acc"], kv[1]["macro_f1"]))
    lines.append(f"Best overall by accuracy/macro F1: **{best[0]}** "
                  f"(acc={best[1]['val_acc']:.4f}, macro_f1={best[1]['macro_f1']:.4f}).")
    reduced_winners = []
    for name, s in summary.items():
        if "no_reduction" in name:
            continue
        ref = rf_base if s["family"] == "rf" else hgb_base
        if (s["val_acc"] >= ref["val_acc"] - 1e-9 and s["macro_f1"] >= ref["macro_f1"] - 1e-9
                and s["total_latency_ms_p95"] <= ref["total_latency_ms_p95"] and s["model_size_kb_mean"] <= ref["model_size_kb_mean"]):
            reduced_winners.append(name)
    if reduced_winners:
        lines.append(f"\nReduced-dimensionality candidates matching/beating their same-classifier no-reduction "
                      f"baseline on accuracy AND macro F1, while being <= on total latency AND size: "
                      f"{', '.join(reduced_winners)}.")
    else:
        lines.append("\nNo reduced-dimensionality candidate matched/beat its same-classifier no-reduction "
                      "baseline on accuracy AND macro F1 while also being <= on latency and size. Dimensionality "
                      "reduction is not recommended for this feature space based on this evidence.")

    md = "\n".join(lines) + "\n"
    results_md.write_text(md, encoding="utf-8")
    print(f"\nComparison table + verdict written -> {results_md}\n")
    print(md)


if __name__ == "__main__":
    main()
