"""
benchmarks/rf_group_oob.py
==========================
Evaluates group-aware Out-Of-Bag (OOB) estimation for the Random Forest posture
model on fold 0 of StratifiedGroupKFold (the production training split).

Calculates:
1. Standard sklearn per-window OOB score on the production model.
2. Strict group-OOB on standard per-window bootstrap (only counting a sample as
   OOB if its entire source sequence was omitted from that tree's bootstrap).
3. Group-bootstrapped Random Forest OOB score (where bootstrapping is performed
   at the sequence_id level, ensuring ~36.8% of sequences are truly held out
   per tree).
"""

import sys
from pathlib import Path
import numpy as np
from joblib import Parallel, delayed

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble._forest import _generate_sample_indices
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from src.posture.rf.rf_trainer import (
    flatten_windows,
    MIN_SAMPLES_LEAF,
    MAX_FEATURES,
    LSTM_DATASET_NPZ,
)


def get_production_data():
    """Load train/val data identical to rf_trainer.py production setup."""
    data = np.load(str(LSTM_DATASET_NPZ), allow_pickle=True)
    X_raw = data["X"].astype(np.float32)
    y_raw = data["y"].astype(np.int32)
    groups_raw = data["groups"]
    classes = data["classes"]

    from sklearn.model_selection import StratifiedGroupKFold
    from src.posture.lstm import lstm_features as lf
    from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X_raw, y_raw, groups_raw))

    X_train_real = X_raw[train_idx]
    y_train_real = y_raw[train_idx]
    groups_train_real = groups_raw[train_idx]

    X_val = X_raw[val_idx]
    y_val = y_raw[val_idx]
    groups_val = groups_raw[val_idx]

    train_col_medians = lf.compute_col_medians(X_train_real)
    X_train_real = lf.impute_nan(X_train_real, train_col_medians)
    X_val = lf.impute_nan(X_val, train_col_medians)

    window_size = X_raw.shape[1]
    X_syn, y_syn, g_syn = generate_synthetic_windows(window_size=window_size, n_per_class=800)
    X_syn = impute_nan(X_syn.astype(np.float32))

    X_train = np.concatenate([X_train_real, X_syn], axis=0).astype(np.float32)
    y_train = np.concatenate([y_train_real, y_syn], axis=0).astype(np.int32)
    groups_train = np.concatenate([groups_train_real, g_syn], axis=0)

    # Shuffling
    rng = np.random.default_rng(seed=1)
    shuf = rng.permutation(len(X_train))
    X_train, y_train, groups_train = X_train[shuf], y_train[shuf], groups_train[shuf]

    X_train_flat = flatten_windows(X_train)
    X_val_flat = flatten_windows(X_val)

    return (
        X_train_flat, y_train, groups_train,
        X_val_flat, y_val, groups_val,
        classes
    )


def compute_standard_and_strict_group_oob(model, X_train, y_train, groups_train, classes):
    """
    Evaluates OOB under standard sklearn model.
    1. Standard window-level OOB score.
    2. Strict group-OOB: sample i is OOB for tree t iff group(i) was NOT in tree t's bootstrap.
    """
    n_samples = X_train.shape[0]
    n_classes = len(classes)

    print("\n[1] Evaluating standard fitted RandomForest...")
    std_oob = getattr(model, "oob_score_", None)
    print(f"  Standard sklearn oob_score_: {std_oob * 100:.2f}%" if std_oob else "  Standard oob_score_: None")

    # Strict Group OOB accumulator
    oob_pred_sum = np.zeros((n_samples, n_classes), dtype=np.float64)
    oob_counts = np.zeros(n_samples, dtype=np.int32)
    tree_omitted_group_counts = []

    print("\n[2] Checking strict group-OOB across trees in standard RF...")
    all_unique_groups = set(groups_train)
    for t_idx, estimator in enumerate(model.estimators_):
        sample_indices = _generate_sample_indices(
            estimator.random_state, n_samples, model._n_samples_bootstrap, model._sample_weight
        )
        sampled_groups = set(groups_train[sample_indices])
        omitted_groups = all_unique_groups - sampled_groups
        tree_omitted_group_counts.append(len(omitted_groups))

        if not omitted_groups:
            continue

        group_oob_mask = np.isin(groups_train, list(omitted_groups))
        group_oob_indices = np.where(group_oob_mask)[0]

        if len(group_oob_indices) == 0:
            continue

        preds = estimator.predict_proba(X_train[group_oob_indices])
        tree_classes = estimator.classes_
        if len(tree_classes) < n_classes:
            full_preds = np.zeros((len(group_oob_indices), n_classes), dtype=np.float64)
            for c_idx, c_val in enumerate(tree_classes):
                full_preds[:, c_val] = preds[:, c_idx]
            preds = full_preds

        oob_pred_sum[group_oob_indices] += preds
        oob_counts[group_oob_indices] += 1

    avg_omitted_groups = np.mean(tree_omitted_group_counts)
    total_covered = int(np.sum(oob_counts > 0))
    print(f"  Average omitted groups per tree (out of {len(all_unique_groups)} total groups): {avg_omitted_groups:.2f}")
    print(f"  Samples with at least one strict group-OOB evaluation: {total_covered} / {n_samples} ({total_covered/n_samples*100:.1f}%)")

    # Real vs synthetic breakdown
    is_real = ~np.char.startswith(groups_train.astype(str), "syn_")
    real_covered = int(np.sum((oob_counts > 0) & is_real))
    n_real = int(np.sum(is_real))
    print(f"  Real samples with at least one strict group-OOB evaluation: {real_covered} / {n_real} ({real_covered/n_real*100:.1f}%)")

    strict_oob_acc = None
    real_strict_oob_acc = None

    if total_covered > 0:
        valid_mask = oob_counts > 0
        final_preds = np.argmax(oob_pred_sum[valid_mask] / oob_counts[valid_mask, None], axis=1)
        strict_oob_acc = float(accuracy_score(y_train[valid_mask], final_preds))
        print(f"  Strict Group-OOB accuracy (on covered samples): {strict_oob_acc * 100:.2f}%")
        if real_covered > 0:
            real_valid_mask = (oob_counts > 0) & is_real
            real_preds = np.argmax(oob_pred_sum[real_valid_mask] / oob_counts[real_valid_mask, None], axis=1)
            real_strict_oob_acc = float(accuracy_score(y_train[real_valid_mask], real_preds))
            print(f"  Strict Group-OOB accuracy on REAL samples only: {real_strict_oob_acc * 100:.2f}%")

    return std_oob, strict_oob_acc, real_strict_oob_acc, avg_omitted_groups, total_covered, real_covered


def _fit_and_eval_tree(t, n_groups, unique_groups, group_to_indices, X_train, y_train, max_features, n_classes, seed):
    rng = np.random.RandomState(seed)
    sampled_group_indices = rng.choice(n_groups, size=n_groups, replace=True)
    sampled_groups = set(unique_groups[sampled_group_indices])
    unsampled_groups = set(unique_groups) - sampled_groups

    tree_train_idx = np.concatenate([group_to_indices[g] for g in sampled_groups])
    tree_oob_idx = np.concatenate([group_to_indices[g] for g in unsampled_groups])

    tree = DecisionTreeClassifier(
        min_samples_leaf=MIN_SAMPLES_LEAF,
        max_features=max_features,
        random_state=rng.randint(0, 1000000),
    )
    tree.fit(X_train[tree_train_idx], y_train[tree_train_idx])

    preds = tree.predict_proba(X_train[tree_oob_idx])
    tree_classes = tree.classes_
    if len(tree_classes) < n_classes:
        full_preds = np.zeros((len(tree_oob_idx), n_classes), dtype=np.float64)
        for c_idx, c_val in enumerate(tree_classes):
            full_preds[:, c_val] = preds[:, c_idx]
        preds = full_preds

    return tree_oob_idx, preds


def compute_group_bootstrapped_rf_oob(X_train, y_train, groups_train, classes, n_estimators=300):
    """
    Trains a group-bootstrapped ensemble where each tree samples sequence groups with replacement.
    This guarantees genuine group-level OOB estimation for every tree and every sample.
    """
    print(f"\n[3] Training Group-Bootstrapped Random Forest ({n_estimators} trees in parallel)...")
    unique_groups = np.unique(groups_train)
    n_groups = len(unique_groups)
    n_samples = len(X_train)
    n_classes = len(classes)

    group_to_indices = {g: np.where(groups_train == g)[0] for g in unique_groups}
    max_features = int(np.ceil(0.1 * X_train.shape[1]))

    # Parallelize tree training
    results = Parallel(n_jobs=-1, verbose=1)(
        delayed(_fit_and_eval_tree)(
            t, n_groups, unique_groups, group_to_indices, X_train, y_train, max_features, n_classes, 42 + t
        )
        for t in range(n_estimators)
    )

    oob_pred_sum = np.zeros((n_samples, n_classes), dtype=np.float64)
    oob_counts = np.zeros(n_samples, dtype=np.int32)

    for tree_oob_idx, preds in results:
        oob_pred_sum[tree_oob_idx] += preds
        oob_counts[tree_oob_idx] += 1

    valid_mask = oob_counts > 0
    final_preds = np.argmax(oob_pred_sum[valid_mask] / oob_counts[valid_mask, None], axis=1)
    group_rf_oob_acc = float(accuracy_score(y_train[valid_mask], final_preds))

    is_real = ~np.char.startswith(groups_train.astype(str), "syn_")
    real_valid_mask = (oob_counts > 0) & is_real
    real_preds = np.argmax(oob_pred_sum[real_valid_mask] / oob_counts[real_valid_mask, None], axis=1)
    real_group_rf_oob_acc = float(accuracy_score(y_train[real_valid_mask], real_preds))

    print(f"  Group-Bootstrapped RF OOB accuracy (overall): {group_rf_oob_acc * 100:.2f}%")
    print(f"  Group-Bootstrapped RF OOB accuracy (REAL only): {real_group_rf_oob_acc * 100:.2f}%")
    print(f"  Average OOB evaluations per sample: {np.mean(oob_counts):.1f} trees")

    return group_rf_oob_acc, real_group_rf_oob_acc


def main():
    print("Loading production training and validation split...")
    X_train, y_train, groups_train, X_val, y_val, groups_val, classes = get_production_data()
    print(f"  Train samples: {X_train.shape[0]}, Val samples: {X_val.shape[0]}")
    print(f"  Unique train groups: {len(np.unique(groups_train))}")

    print("\nTraining production RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        max_features=MAX_FEATURES,
        oob_score=True,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    val_acc = model.score(X_val, y_val)
    print(f"  Train Accuracy      : {train_acc * 100:.2f}%")
    print(f"  Validation Accuracy : {val_acc * 100:.2f}%")

    std_oob, strict_oob, real_strict_oob, avg_omitted, total_cov, real_cov = compute_standard_and_strict_group_oob(
        model, X_train, y_train, groups_train, classes
    )

    grp_rf_oob, grp_rf_real_oob = compute_group_bootstrapped_rf_oob(
        X_train, y_train, groups_train, classes, n_estimators=300
    )

    print("\n" + "=" * 80)
    print("GROUP-AWARE OOB INVESTIGATION SUMMARY")
    print("=" * 80)
    print(f"Train Accuracy (all real+syn)         : {train_acc * 100:.2f}%")
    print(f"Validation Accuracy (real only)       : {val_acc * 100:.2f}%")
    print(f"Standard Sklearn OOB Score            : {std_oob * 100:.2f}%")
    if strict_oob is not None:
        print(f"Strict Group-OOB (Standard RF, cov)   : {strict_oob * 100:.2f}% (covered {total_cov}/{len(X_train)})")
    if real_strict_oob is not None:
        print(f"Strict Group-OOB (Standard RF, real)  : {real_strict_oob * 100:.2f}% (covered {real_cov}/{np.sum(~np.char.startswith(groups_train.astype(str), 'syn_'))})")
    else:
        print(f"Strict Group-OOB (Standard RF, real)  : N/A (0 real sequences held out across all 300 trees)")
    print(f"Group-Bootstrapped RF OOB (all)       : {grp_rf_oob * 100:.2f}%")
    print(f"Group-Bootstrapped RF OOB (REAL only) : {grp_rf_real_oob * 100:.2f}%")
    print("=" * 80)


if __name__ == "__main__":
    main()
