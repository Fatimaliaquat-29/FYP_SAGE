"""
benchmarks/rf_methodology_sweep.py
===================================
Offline (validation-split) screening pass for RF methodology candidates
from the RF-generalization improvement loop, following the exact
methodology docs/RF_GENERALIZATION_INVESTIGATION.md already established
for this decision: a multi-fold, GROUP-aware CV (StratifiedGroupKFold by
sequence_id, never by window) on data/lstm_dataset.npz, screening many
candidates cheaply, before spending real-footage evaluation time only on
whatever survives this screen. This script never touches test_footage/ --
see benchmarks/rf_methodology_realfootage_confirm.py for the decisive
real-footage confirmation step (this project's own established rule: a
validation-split win is not adopted until real-footage-confirmed).

Candidates (see docs/RF_GENERALIZATION_INVESTIGATION.md Section 3's root
cause -- 56 independent real sequences vs. 3,960 flattened features -- for
why these were chosen):
  - ccp_alpha cost-complexity pruning (never tried before; max_leaf_nodes
    was tried and rejected, which is a different mechanism)
  - max_depth / min_samples_split sweeps (not tried in isolation before --
    only combined with the already-adopted min_samples_leaf/max_features)
  - GradientBoostingClassifier as an alternative ensemble
  - PCA dimensionality reduction on the flattened 3,960-dim representation

Usage:
    python benchmarks/rf_methodology_sweep.py
"""
import sys
import time
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.posture.rf.rf_trainer import flatten_windows, MIN_SAMPLES_LEAF, MAX_FEATURES
from src.posture.lstm import lstm_features as lf
from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan

LSTM_DATASET_NPZ = REPO_ROOT / "data" / "lstm_dataset.npz"
N_FOLDS = 5


def load_folds():
    """Yields (X_train_flat, y_train, X_val_flat, y_val, classes) for each
    of N_FOLDS StratifiedGroupKFold splits -- same split scheme/seed as
    rf_trainer.py::train(), just iterating every fold instead of only
    fold 0, matching docs/RF_GENERALIZATION_INVESTIGATION.md's own 5-fold
    screening methodology."""
    from sklearn.model_selection import StratifiedGroupKFold

    data = np.load(str(LSTM_DATASET_NPZ), allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int32)
    groups = data["groups"]
    classes = data["classes"]
    window_size = X.shape[1]

    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
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


def _metrics(y_val, y_pred, y_train_acc):
    from sklearn.metrics import f1_score, balanced_accuracy_score, accuracy_score
    val_acc = accuracy_score(y_val, y_pred)
    return {
        "val_acc": val_acc,
        "macro_f1": f1_score(y_val, y_pred, average="macro", zero_division=0),
        "balanced_acc": balanced_accuracy_score(y_val, y_pred),
        "gap": y_train_acc - val_acc,
    }


def make_candidates():
    """Returns {name: fit_fn(X_train, y_train) -> fitted sklearn-style model}."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.decomposition import PCA
    from sklearn.pipeline import make_pipeline

    candidates = {}

    candidates["baseline (production: leaf=20, max_features=0.1)"] = lambda: RandomForestClassifier(
        n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
        n_jobs=-1, random_state=42,
    )

    for alpha in (1e-4, 5e-4, 1e-3, 2e-3):
        candidates[f"ccp_alpha={alpha}"] = (lambda a=alpha: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
            ccp_alpha=a, n_jobs=-1, random_state=42,
        ))

    for depth in (10, 15, 20):
        candidates[f"max_depth={depth}"] = (lambda d=depth: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
            max_depth=d, n_jobs=-1, random_state=42,
        ))

    for mss in (10, 20, 40):
        candidates[f"min_samples_split={mss}"] = (lambda m=mss: RandomForestClassifier(
            n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF, max_features=MAX_FEATURES,
            min_samples_split=m, n_jobs=-1, random_state=42,
        ))

    # GradientBoostingClassifier was tried and dropped after one real fit:
    # 5651s (~94 min) for a single candidate on this dataset (3,960 features
    # x ~11.7k samples) vs. ~155s for the equivalent RF fit -- ~36x slower,
    # because sklearn's GradientBoostingClassifier has no n_jobs and builds
    # trees sequentially. At that rate the 2 GB candidates x 5 folds alone
    # would cost ~15+ hours, which was judged not worth it given this
    # project's own established preference for evidence gathered in
    # reasonable time over exhaustiveness -- an honest, evidence-based
    # rejection on cost grounds (this dataset/environment), not a claim
    # that boosting couldn't work at all with a smaller estimator count.

    for k in (50, 100, 200):
        candidates[f"pca(n={k})+rf"] = (lambda k=k: make_pipeline(
            PCA(n_components=k, random_state=42),
            RandomForestClassifier(n_estimators=300, min_samples_leaf=MIN_SAMPLES_LEAF,
                                    max_features=MAX_FEATURES, n_jobs=-1, random_state=42),
        ))

    return candidates


def main():
    print(f"Loading dataset from {LSTM_DATASET_NPZ}...")
    candidates = make_candidates()
    # {name: [per-fold metric dicts]}
    results = {name: [] for name in candidates}
    fold_times = {name: [] for name in candidates}

    for fold_i, X_train, y_train, X_val, y_val, classes in load_folds():
        print(f"\n=== Fold {fold_i} (train={len(X_train)}, val={len(X_val)}) ===")
        for name, make_model in candidates.items():
            t0 = time.perf_counter()
            model = make_model()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            y_train_acc = model.score(X_train, y_train)
            m = _metrics(y_val, y_pred, y_train_acc)
            dt = time.perf_counter() - t0
            results[name].append(m)
            fold_times[name].append(dt)
            print(f"  {name:<45} val_acc={m['val_acc']:.4f} macro_f1={m['macro_f1']:.4f} "
                  f"bal_acc={m['balanced_acc']:.4f} gap={m['gap']:.4f}  ({dt:.1f}s)")

    print(f"\n{'='*100}\nSUMMARY (mean over {N_FOLDS} folds)\n{'='*100}")
    print(f"{'candidate':<45}{'val_acc':>10}{'macro_f1':>10}{'bal_acc':>10}{'gap':>10}{'mean_s':>9}")
    baseline_name = "baseline (production: leaf=20, max_features=0.1)"
    baseline_acc = np.mean([m["val_acc"] for m in results[baseline_name]])
    baseline_f1 = np.mean([m["macro_f1"] for m in results[baseline_name]])
    for name, fold_results in results.items():
        acc = np.mean([m["val_acc"] for m in fold_results])
        f1 = np.mean([m["macro_f1"] for m in fold_results])
        bal = np.mean([m["balanced_acc"] for m in fold_results])
        gap = np.mean([m["gap"] for m in fold_results])
        t = np.mean(fold_times[name])
        marker = ""
        if name != baseline_name:
            if acc > baseline_acc + 0.01 and f1 > baseline_f1:
                marker = "  <-- beats baseline on both acc and F1 (candidate for real-footage confirm)"
        print(f"{name:<45}{acc:>10.4f}{f1:>10.4f}{bal:>10.4f}{gap:>10.4f}{t:>9.1f}{marker}")


if __name__ == "__main__":
    main()
