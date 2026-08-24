"""
benchmarks/rf_alternatives_full_sweep.py
=========================================
Round 2 of the RF-alternative candidate screen. Round 1
(benchmarks/rf_methodology_sweep.py) rejected GradientBoostingClassifier
on raw fit-time alone (5651s / ~94min for one fit vs ~155s for the RF
baseline) before any deployment-relevant metric was measured, and never
persisted its results anywhere durable -- only a wall-clock number
survived, in a code comment, with no record of the exact config used.
This script fixes that:

  1. Implementation: HistGradientBoostingClassifier (sklearn's
     histogram-binned, natively multithreaded GB implementation, already
     available in the installed sklearn==1.9.0 -- no new dependency)
     instead of the sequential, no-n_jobs GradientBoostingClassifier that
     produced the 94-minute fit.
  2. Metrics: every candidate -- RF baseline, every previously-tried RF
     pruning/depth/split/PCA variant, AND every HistGB config in this
     round's sweep -- is instrumented identically for accuracy, macro F1,
     fit time (reference only, NOT a rejection criterion by itself),
     predict-ONLY latency (single-row calls, matching how
     src/posture/rf/rf_classifier.py actually invokes predict_proba in
     real-time use -- one (1, n_features) row per video frame, never a
     batch), and serialized (joblib) model size.
  3. Persistence: results are written to disk INCREMENTALLY -- after
     every single candidate-fold fit, not just at the end -- to
     benchmarks/results/rf_alternatives_{full,quick}_sweep.json (atomic
     write: temp file + os.replace, so a kill mid-write can never leave a
     half-written/corrupt JSON on disk), plus a human-readable
     benchmarks/results/rf_alternatives_{full,quick}_comparison.md once
     complete.

ROUND 2b -- interruptibility (this project's own actual experience: round
2's first attempt at this full sweep was deliberately interrupted after 4
of 120 candidate-fold fits to add exactly this): a full 5-fold x 24-candidate
sweep costs ~6-7 hours of wall-clock CPU time on this machine. This script
is now:
  - RESUMABLE: on start, if a results file exists whose candidate set +
    fold count + quick-mode flag exactly match this invocation (see
    candidate_signature()) and its status is "in_progress", already-
    completed (candidate, fold) pairs are loaded and skipped -- only
    whatever's missing gets (re)computed. A "complete" prior run, or one
    with a different signature, is left alone and a fresh run starts
    (use --fresh to force a fresh run even over a matching in-progress one).
  - QUICK-PASS capable (--quick): 2 folds instead of 5, and a coarser
    subset of the SAME candidates make_candidates() defines (endpoints of
    each swept axis rather than every point) -- for a fast rough read.
    This does NOT alter any hyperparameter VALUE from make_candidates()'s
    definitions (see round 1/2's own established rule: methodology
    stays fixed, only which subset of already-defined configs runs in
    quick mode) -- see QUICK_CANDIDATE_NAMES below. Quick and full runs
    write to separate result files so one can never clobber the other.
  - SELF-ESTIMATING: after every fold, prints a wall-clock ETA (average
    per-candidate time over whatever was newly fit in this run x however
    many candidate-fold pairs remain) so a full run's total cost is known
    before you're deep into it, not just guessed at up front.

Data/leakage guarantees are UNCHANGED from round 1 (see
docs/RF_GENERALIZATION_INVESTIGATION.md for the established methodology
this follows): real data only from data/lstm_dataset.npz,
StratifiedGroupKFold grouped by sequence_id (never by window), post-split
synthetic augmentation injected into the train fold only, train-fold-only
median imputation. src/gait/* and test_footage/ are not touched by this
script -- test_footage is reserved for the separate, decisive real-footage
confirmation step (rf_methodology_realfootage_confirm.py), run only if a
candidate clears the bar this script's own printed verdict sets out.

Usage:
    python benchmarks/rf_alternatives_full_sweep.py               # full 5-fold, all 24 candidates, resumes if possible
    python benchmarks/rf_alternatives_full_sweep.py --quick        # 2-fold, 13-candidate rough read
    python benchmarks/rf_alternatives_full_sweep.py --fresh        # ignore any existing in-progress state, start over
    python benchmarks/rf_alternatives_full_sweep.py --folds 3      # override fold count directly
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.rf.rf_trainer import flatten_windows, MIN_SAMPLES_LEAF, MAX_FEATURES
from src.posture.lstm import lstm_features as lf
from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan

LSTM_DATASET_NPZ = REPO_ROOT / "data" / "lstm_dataset.npz"
RESULTS_DIR = REPO_ROOT / "benchmarks" / "results"
DEFAULT_N_FOLDS = 5
QUICK_N_FOLDS = 2
N_LATENCY_SAMPLES = 200
BASELINE_NAME = "rf_baseline (production: leaf=20, max_features=0.1)"

# Coarser subset for --quick: endpoints of each swept axis from
# make_candidates() below, not new/different values. See module docstring.
QUICK_CANDIDATE_NAMES = {
    BASELINE_NAME,
    "ccp_alpha=0.0001", "ccp_alpha=0.002",
    "max_depth=10", "max_depth=20",
    "min_samples_split=10", "min_samples_split=40",
    "pca(n=100)+rf",
    "hgb_default (max_iter=200,lr=0.1,depth=None,l2=0)",
    "hgb_max_iter=300",
    "hgb_learning_rate=0.3",
    "hgb_max_depth=10",
    "hgb_l2_regularization=1.0",
}


def load_folds(n_folds: int):
    """Yields (fold_i, X_train_flat, y_train, X_val_flat, y_val, classes)
    for each of n_folds StratifiedGroupKFold splits -- identical split
    scheme/seed to benchmarks/rf_methodology_sweep.py::load_folds()
    (round 1) when n_folds=5, so round 2's numbers are directly
    comparable, not just re-derived. n_folds is parameterized (not fixed
    at 5) only to support --quick/--folds; it still always changes
    n_splits on the SAME StratifiedGroupKFold call, never the underlying
    data/grouping/leakage-guard logic."""
    from sklearn.model_selection import StratifiedGroupKFold

    data = np.load(str(LSTM_DATASET_NPZ), allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int32)
    groups = data["groups"]
    classes = data["classes"]
    window_size = X.shape[1]

    sgkf = StratifiedGroupKFold(n_splits=n_folds, shuffle=True, random_state=42)
    for fold_i, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups)):
        X_val, y_val = X[val_idx], y[val_idx]
        X_train, y_train = X[train_idx], y[train_idx]

        train_col_medians = lf.compute_col_medians(X_train)
        X_train = lf.impute_nan(X_train, train_col_medians)
        X_val = lf.impute_nan(X_val, train_col_medians)

        X_syn, y_syn, _ = generate_synthetic_windows(window_size=window_size, n_per_class=800)
        X_syn = impute_nan(X_syn.astype(np.float32))
        X_train = np.concatenate([X_train, X_syn], axis=0).astype(np.float32)
        y_train = np.concatenate([y_train, y_syn], axis=0).astype(np.int32)
        rng = np.random.default_rng(seed=1)
        shuf = rng.permutation(len(X_train))
        X_train, y_train = X_train[shuf], y_train[shuf]

        X_train_flat = flatten_windows(X_train)
        X_val_flat = flatten_windows(X_val)
        yield fold_i, X_train_flat, y_train, X_val_flat, y_val, classes


def make_candidates():
    """Returns {name: (family, config_dict, fit_fn)}. UNCHANGED from the
    first (interrupted) round-2 run -- see module docstring's
    interruptibility section for why this function itself is never
    touched by --quick: quick mode filters this dict's OUTPUT
    (QUICK_CANDIDATE_NAMES), it never edits the values defined here.

    family is one of "rf" / "pca_rf" / "hgb" -- used to decide how to
    force single-threaded inference before timing predict latency (see
    _measure_predict_latency_ms), matching how each family would actually
    be deployed.

    RF-family candidates (rf_baseline, ccp_alpha, max_depth,
    min_samples_split, PCA+RF) are the exact same configs round 1's
    benchmarks/rf_methodology_sweep.py tried -- reproduced here, not
    reused, since round 1 never persisted fitted models or per-candidate
    results anywhere they could be reloaded from.

    HistGB candidates: a one-at-a-time sweep from a sensible default
    center (max_iter=200, learning_rate=0.1, max_depth=None,
    l2_regularization=0.0), varying each of the four requested axes
    independently -- the same one-factor-at-a-time design round 1 used
    for ccp_alpha/max_depth/min_samples_split, rather than a full 4x4x3x4
    factorial grid, which at ~150-250s/fit would cost many hours for
    negligible extra signal over what a full grid would show. Every
    config uses early_stopping=True (validation_fraction=0.1,
    n_iter_no_change=10) so max_iter acts as a ceiling, not a fixed cost
    -- directly addressing round 1's "was a reduced/early-stopped fit
    ever tried" gap.
    """
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.decomposition import PCA
    from sklearn.pipeline import make_pipeline

    candidates = {}

    def rf(**kw):
        params = dict(n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
                       n_jobs=-1, random_state=42)
        params.update(kw)
        return params, lambda p=params: RandomForestClassifier(**p)

    cfg, fn = rf()
    candidates[BASELINE_NAME] = ("rf", cfg, fn)

    for alpha in (1e-4, 5e-4, 1e-3, 2e-3):
        cfg, fn = rf(ccp_alpha=alpha)
        candidates[f"ccp_alpha={alpha}"] = ("rf", cfg, fn)

    for depth in (10, 15, 20):
        cfg, fn = rf(max_depth=depth)
        candidates[f"max_depth={depth}"] = ("rf", cfg, fn)

    for mss in (10, 20, 40):
        cfg, fn = rf(min_samples_split=mss)
        candidates[f"min_samples_split={mss}"] = ("rf", cfg, fn)

    for k in (50, 100, 200):
        rf_cfg = dict(n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
                       n_jobs=-1, random_state=42)
        cfg = {"pca_n_components": k, **rf_cfg}
        candidates[f"pca(n={k})+rf"] = (
            "pca_rf", cfg,
            lambda k=k, rf_cfg=rf_cfg: make_pipeline(
                PCA(n_components=k, random_state=42),
                RandomForestClassifier(**rf_cfg),
            ),
        )

    def hgb(**kw):
        params = dict(max_iter=200, learning_rate=0.1, max_depth=None, l2_regularization=0.0,
                       early_stopping=True, validation_fraction=0.1, n_iter_no_change=10, random_state=42)
        params.update(kw)
        return params, lambda p=params: HistGradientBoostingClassifier(**p)

    cfg, fn = hgb()
    candidates["hgb_default (max_iter=200,lr=0.1,depth=None,l2=0)"] = ("hgb", cfg, fn)

    for mi in (50, 100, 300):
        cfg, fn = hgb(max_iter=mi)
        candidates[f"hgb_max_iter={mi}"] = ("hgb", cfg, fn)

    for lr in (0.03, 0.3):
        cfg, fn = hgb(learning_rate=lr)
        candidates[f"hgb_learning_rate={lr}"] = ("hgb", cfg, fn)

    for depth in (5, 10):
        cfg, fn = hgb(max_depth=depth)
        candidates[f"hgb_max_depth={depth}"] = ("hgb", cfg, fn)

    for l2 in (0.1, 1.0):
        cfg, fn = hgb(l2_regularization=l2)
        candidates[f"hgb_l2_regularization={l2}"] = ("hgb", cfg, fn)

    return candidates


def _measure_predict_latency_ms(model, family, X_val_flat, rng):
    """Single-row predict_proba() calls -- the actual unit of real-time
    inference (src/posture/rf/rf_classifier.py:242 calls predict_proba on
    one (1, n_features) row per video frame, never a batch), NOT a
    batched/vectorized timing, which would understate real per-frame cost.

    For RF-family models (plain RF and PCA+RF pipelines), n_jobs is
    forced to 1 before timing, mirroring rf_classifier.py's own forced
    single-threaded inference (that file's comment: spinning up a joblib
    worker pool per single-row call is pure overhead with nothing to
    parallelize, and was observed there to make frame-by-frame inference
    catastrophically slow). HistGradientBoostingClassifier has no n_jobs
    constructor param to force the same way; timed as-is under its
    default internal threading. This is a real, flagged asymmetry -- not
    a fully controlled comparison on this one axis -- called out again in
    the final report rather than papered over.
    """
    if family == "rf":
        model.n_jobs = 1
    elif family == "pca_rf":
        model.named_steps["randomforestclassifier"].n_jobs = 1

    n = min(N_LATENCY_SAMPLES, X_val_flat.shape[0])
    idx = rng.choice(X_val_flat.shape[0], size=n, replace=False)
    times_ms = []
    for i in idx:
        row = X_val_flat[i:i + 1]
        t0 = time.perf_counter()
        model.predict_proba(row)
        times_ms.append((time.perf_counter() - t0) * 1000.0)
    return times_ms


def _model_size_kb(model, tmp_dir: Path) -> float:
    import joblib
    probe_path = tmp_dir / "size_probe.joblib"
    joblib.dump(model, str(probe_path))
    size_kb = probe_path.stat().st_size / 1024.0
    probe_path.unlink()
    return size_kb


def _metrics(y_val, y_pred, y_train_acc):
    from sklearn.metrics import f1_score, balanced_accuracy_score, accuracy_score
    val_acc = accuracy_score(y_val, y_pred)
    return {
        "val_acc": val_acc,
        "macro_f1": f1_score(y_val, y_pred, average="macro", zero_division=0),
        "balanced_acc": balanced_accuracy_score(y_val, y_pred),
        "gap": y_train_acc - val_acc,
    }


def candidate_signature(candidates: dict, n_folds: int, quick: bool) -> str:
    """Fingerprints exactly what this run would compute (candidate names +
    configs + fold count + quick flag) so a resume only ever picks up a
    prior run of the IDENTICAL sweep -- never silently mixes results from
    a differently-configured run."""
    payload = json.dumps(
        {name: cfg for name, (_family, cfg, _fn) in sorted(candidates.items())},
        sort_keys=True,
    ) + f"|folds={n_folds}|quick={quick}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _atomic_write_json(path: Path, obj: dict) -> None:
    """Write via temp-file + os.replace so a kill mid-write can never
    leave a half-written/corrupt results file on disk -- os.replace is
    atomic on the same filesystem, so readers only ever see the old
    complete file or the new complete file, never a partial one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(path))


def quick_filter_candidates(candidates: dict) -> dict:
    filtered = {name: c for name, c in candidates.items() if name in QUICK_CANDIDATE_NAMES}
    missing = QUICK_CANDIDATE_NAMES - set(filtered)
    if missing:
        raise ValueError(f"QUICK_CANDIDATE_NAMES references candidates make_candidates() no longer defines: {missing}")
    return filtered


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true",
                         help=f"{QUICK_N_FOLDS}-fold, {len(QUICK_CANDIDATE_NAMES)}-candidate rough read instead of the full sweep")
    parser.add_argument("--folds", type=int, default=None, help="Override fold count directly")
    parser.add_argument("--fresh", action="store_true", help="Ignore any existing in-progress state and start over")
    args = parser.parse_args()

    quick = args.quick
    n_folds = args.folds if args.folds is not None else (QUICK_N_FOLDS if quick else DEFAULT_N_FOLDS)

    results_json = RESULTS_DIR / f"rf_alternatives_{'quick' if quick else 'full'}_sweep.json"
    results_md = RESULTS_DIR / f"rf_alternatives_{'quick' if quick else 'full'}_comparison.md"

    print(f"Loading dataset from {LSTM_DATASET_NPZ}...")
    candidates = make_candidates()
    if quick:
        candidates = quick_filter_candidates(candidates)
    sig = candidate_signature(candidates, n_folds, quick)
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
                print(f"Resuming in-progress run (signature {sig}): {done}/{total_pairs} "
                      f"candidate-fold results already on disk, continuing from there.")
            elif existing.get("candidate_signature") != sig:
                print(f"Existing {results_json.name} is from a differently-configured run "
                      f"(signature {existing.get('candidate_signature')} != {sig}) -- starting fresh "
                      f"(old file will be overwritten once this run saves).")
            else:
                print(f"Existing {results_json.name} status is {existing.get('status')!r}, not resumable "
                      f"-- starting fresh. Pass --fresh to suppress this message.")

    if raw is None:
        raw = {name: {"family": family, "config": cfg, "folds": []} for name, (family, cfg, _fn) in candidates.items()}
        started_at = datetime.now(timezone.utc).isoformat()

    completed_pairs = {(name, f["fold"]) for name, rec in raw.items() for f in rec["folds"]}

    def save_in_progress():
        _atomic_write_json(results_json, {
            "status": "in_progress",
            "candidate_signature": sig,
            "n_folds": n_folds,
            "quick_mode": quick,
            "n_latency_samples_per_fold": N_LATENCY_SAMPLES,
            "baseline_name": BASELINE_NAME,
            "started_at": started_at,
            "last_updated_at": datetime.now(timezone.utc).isoformat(),
            "raw_per_fold": raw,
        })

    save_in_progress()  # persist skeleton immediately -- even a kill before the first fit finishes leaves a valid, resumable file
    print(f"{len(candidates)} candidates x {n_folds} folds ({'QUICK' if quick else 'FULL'} mode). "
          f"{len(completed_pairs)}/{total_pairs} candidate-fold results already complete.\n")

    rng = np.random.default_rng(seed=123)
    newly_fit_times = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for fold_i, X_train, y_train, X_val, y_val, classes in load_folds(n_folds):
            print(f"\n=== Fold {fold_i} (train={len(X_train)}, val={len(X_val)}) ===")
            for name, (family, cfg, make_model) in candidates.items():
                if (name, fold_i) in completed_pairs:
                    print(f"  {name:<50} [skip -- already completed]")
                    continue

                cand_t0 = time.perf_counter()
                t0 = time.perf_counter()
                model = make_model()
                model.fit(X_train, y_train)
                fit_time = time.perf_counter() - t0

                y_pred = model.predict(X_val)
                y_train_acc = model.score(X_train, y_train)
                m = _metrics(y_val, y_pred, y_train_acc)

                latency_ms = _measure_predict_latency_ms(model, family, X_val, rng)
                size_kb = _model_size_kb(model, tmp_dir)

                fold_record = {
                    "fold": fold_i,
                    **m,
                    "fit_time_s": fit_time,
                    "predict_latency_ms_mean": float(np.mean(latency_ms)),
                    "predict_latency_ms_p95": float(np.percentile(latency_ms, 95)),
                    "model_size_kb": size_kb,
                }
                if family == "hgb":
                    fold_record["n_iter_actual"] = int(model.n_iter_)
                raw[name]["folds"].append(fold_record)
                save_in_progress()
                newly_fit_times.append(time.perf_counter() - cand_t0)

                print(f"  {name:<50} val_acc={m['val_acc']:.4f} macro_f1={m['macro_f1']:.4f} "
                      f"fit={fit_time:6.1f}s  pred_p95={fold_record['predict_latency_ms_p95']:6.2f}ms  "
                      f"size={size_kb:8.1f}KB")

            done = sum(len(v["folds"]) for v in raw.values())
            remaining = total_pairs - done
            if newly_fit_times and remaining > 0:
                avg = sum(newly_fit_times) / len(newly_fit_times)
                eta_s = avg * remaining
                eta_finish = datetime.now().astimezone() + timedelta(seconds=eta_s)
                print(f"\n[ETA] {done}/{total_pairs} done, avg {avg:.1f}s/candidate over {len(newly_fit_times)} "
                      f"newly-fit this run. ~{eta_s/3600:.2f}h remaining, "
                      f"estimated finish ~{eta_finish.strftime('%Y-%m-%d %H:%M')}.\n")

    # ── Aggregate across folds ──────────────────────────────────────────
    summary = {}
    for name, rec in raw.items():
        folds = rec["folds"]
        summary[name] = {
            "family": rec["family"],
            "config": rec["config"],
            "val_acc": float(np.mean([f["val_acc"] for f in folds])),
            "macro_f1": float(np.mean([f["macro_f1"] for f in folds])),
            "balanced_acc": float(np.mean([f["balanced_acc"] for f in folds])),
            "gap": float(np.mean([f["gap"] for f in folds])),
            "fit_time_s_mean": float(np.mean([f["fit_time_s"] for f in folds])),
            "predict_latency_ms_mean": float(np.mean([f["predict_latency_ms_mean"] for f in folds])),
            "predict_latency_ms_p95": float(np.mean([f["predict_latency_ms_p95"] for f in folds])),
            "model_size_kb_mean": float(np.mean([f["model_size_kb"] for f in folds])),
        }

    _atomic_write_json(results_json, {
        "status": "complete",
        "candidate_signature": sig,
        "n_folds": n_folds,
        "quick_mode": quick,
        "n_latency_samples_per_fold": N_LATENCY_SAMPLES,
        "baseline_name": BASELINE_NAME,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "raw_per_fold": raw,
        "summary": summary,
    })
    print(f"\nFull per-fold results written -> {results_json}")

    # ── Comparison table + verdict ──────────────────────────────────────
    baseline = summary[BASELINE_NAME]
    lines = []
    lines.append(f"# RF-alternatives comparison ({'quick' if quick else 'full'} run, {n_folds}-fold)\n")
    lines.append(f"StratifiedGroupKFold (grouped by sequence_id), {N_LATENCY_SAMPLES} single-row "
                  f"predict_proba() calls/fold for latency, joblib-serialized size/fold. "
                  f"RF-family predict latency measured with n_jobs forced to 1 (matches production "
                  f"src/posture/rf/rf_classifier.py); HistGB has no equivalent knob, timed as-is "
                  f"under default threading -- not a fully controlled comparison on that one axis.\n")
    header = ("| Candidate | Family | Accuracy | Macro F1 | Fit time (s) | "
              "Predict latency mean/p95 (ms) | Model size (KB) |")
    sep = "|---|---|---|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for name, s in summary.items():
        marker = " **(baseline)**" if name == BASELINE_NAME else ""
        lines.append(
            f"| {name}{marker} | {s['family']} | {s['val_acc']:.4f} | {s['macro_f1']:.4f} | "
            f"{s['fit_time_s_mean']:.1f} | {s['predict_latency_ms_mean']:.3f} / {s['predict_latency_ms_p95']:.3f} | "
            f"{s['model_size_kb_mean']:.1f} |"
        )

    lines.append("\n## Verdict\n")
    winners = []
    for name, s in summary.items():
        if s["family"] != "hgb":
            continue
        clears = (
            s["val_acc"] >= baseline["val_acc"] - 1e-9
            and s["macro_f1"] >= baseline["macro_f1"] - 1e-9
            and s["predict_latency_ms_p95"] <= baseline["predict_latency_ms_p95"]
            and s["model_size_kb_mean"] <= baseline["model_size_kb_mean"]
        )
        if clears:
            winners.append(name)

    if winners:
        lines.append(f"Candidate(s) matching/beating RF baseline on accuracy AND macro F1 while being "
                      f"equal-or-better on BOTH predict latency and model size: {', '.join(winners)}.")
        lines.append("These require real-footage confirmation "
                      "(benchmarks/rf_methodology_realfootage_confirm.py) before being treated as a real result.")
    else:
        lines.append("No HistGradientBoostingClassifier candidate cleared the bar (>= RF baseline on "
                      "accuracy AND macro F1, AND <= baseline on both predict latency p95 and model size). "
                      "Shipped model (models/rf_posture.joblib) is left unchanged.")
        hgb_summaries = [s for s in summary.values() if s["family"] == "hgb"]
        if hgb_summaries:
            best_hgb = max(hgb_summaries, key=lambda s: (s["val_acc"], s["macro_f1"]))
            best_hgb_name = [n for n, s in summary.items() if s is best_hgb][0]
            lines.append("\nPer-candidate reasons (best HistGB config vs baseline):")
            lines.append(f"- Best HistGB candidate by accuracy: {best_hgb_name}")
            lines.append(f"  - accuracy {best_hgb['val_acc']:.4f} vs baseline {baseline['val_acc']:.4f}")
            lines.append(f"  - macro F1 {best_hgb['macro_f1']:.4f} vs baseline {baseline['macro_f1']:.4f}")
            lines.append(f"  - predict p95 {best_hgb['predict_latency_ms_p95']:.3f}ms vs baseline "
                          f"{baseline['predict_latency_ms_p95']:.3f}ms")
            lines.append(f"  - model size {best_hgb['model_size_kb_mean']:.1f}KB vs baseline "
                          f"{baseline['model_size_kb_mean']:.1f}KB")

    md = "\n".join(lines) + "\n"
    results_md.write_text(md, encoding="utf-8")
    print(f"\nComparison table + verdict written -> {results_md}\n")
    print(md)


if __name__ == "__main__":
    main()
