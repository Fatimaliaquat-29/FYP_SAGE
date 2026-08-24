"""
rf_trainer.py
=============
Trains a Random Forest classifier on the SAME sliding-window pose keypoint
dataset used by the LSTM/TCN (data/lstm_dataset.npz), reusing the identical
data loading, grouped train/val split, and post-split synthetic-augmentation
injection as tcn_trainer.py/lstm_trainer.py, so all three models are trained
and validated on exactly the same data.

The only difference from the sequence models: a Random Forest has no notion
of a time axis, so each (window_size, 132) window of
normalized-position-plus-velocity features (see
src/posture/lstm/lstm_features.py) is reduced to a single feature vector
before fitting -- either by flattening every frame (FEATURE_REPRESENTATION
="flatten", the original approach) or by summarizing each of the 132
features' distribution across the window (="summary" -- mean/std/min/max/
last-frame-value = 5x132=660 dims, the current default; see the
FEATURE_REPRESENTATION constant below for why).

Usage:
    python src/posture/rf/rf_trainer.py [--n-estimators 300]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA_DIR = REPO_ROOT / "data"
MODELS_DIR = REPO_ROOT / "models"
LSTM_DATASET_NPZ = DATA_DIR / "lstm_dataset.npz"
RF_MODEL_PATH = MODELS_DIR / "rf_posture.joblib"
RF_ENCODER_PATH = MODELS_DIR / "rf_label_encoder.json"


def flatten_windows(X: np.ndarray) -> np.ndarray:
    """(N, window_size, n_features) -> (N, window_size * n_features)."""
    return X.reshape(X.shape[0], -1)


def summarize_windows(X: np.ndarray) -> np.ndarray:
    """
    (N, window_size, n_features) -> (N, n_features * 5): mean/std/min/max/
    last-frame-value of each of the 132 raw features across the window's
    time axis, instead of every individual frame value.

    Root-cause motivation (see docs/RF_GENERALIZATION_INVESTIGATION.md for
    the full diagnosis): flattening hands the model 3,960 features built
    from only ~56 independent real training SEQUENCES (each contributing
    dozens of heavily time-autocorrelated sliding windows) -- a classic
    high-dimension/low-independent-sample setup for a tree ensemble that
    treats every window as i.i.d. Feature-importance was diffuse (no single
    leaky feature), so the fix is reducing dimensionality, not removing a
    culprit. A 5-fold group-aware CV (not a single split, to avoid
    overfitting the choice itself to one split) confirmed this representation
    improves validation accuracy, macro F1, AND balanced accuracy over the
    flattened one, and it was then separately confirmed on real footage
    (not just the validation split) before being made the default.
    """
    mean = X.mean(axis=1)
    std = X.std(axis=1)
    mn = X.min(axis=1)
    mx = X.max(axis=1)
    last = X[:, -1, :]
    return np.concatenate([mean, std, mn, mx, last], axis=1).astype(np.float32)


FEATURE_REPRESENTATIONS = {"flatten": flatten_windows, "summary": summarize_windows}

# See summarize_windows()'s docstring for the diagnosis motivating this
# option, and docs/RF_GENERALIZATION_INVESTIGATION.md for the full
# comparison. TESTED AND REJECTED as the default: a 5-fold group-aware CV
# on the validation split alone showed "summary" beating "flatten" on
# every metric (accuracy, macro F1, balanced accuracy), which looked like
# a genuine win -- but confirmed on real footage (this project's actual
# decisive test, per repeated prior experience with validation-split
# conclusions not holding up), "summary" LOST clearly on the harder
# Hussain set (57.1% vs 69.2% accuracy, worse macro F1 and macro recall,
# more false alarms) and was roughly a wash on the easier Sanawar set.
# "flatten" remains the default; "summary" is kept as a documented,
# available-but-not-recommended option, not deleted, since the underlying
# diagnosis (too few independent real sequences relative to 3960 flattened
# features) is still believed correct -- this particular remedy just did
# not survive contact with real footage.
FEATURE_REPRESENTATION = "flatten"



# Chosen via a 10-config pruning sweep on data/lstm_dataset.npz (max_depth in
# {10,15,20}, min_samples_leaf in {10,20}, ccp_alpha in {5e-4,1e-3}, and a
# combined depth+leaf+fewer-trees config), confirmed on both real-footage
# test sets (not just the validation split -- see docs/TCN_IMPLEMENTATION_NOTES.md
# for why validation-split-only tuning is not trusted on this project).
# min_samples_leaf=20 alone won outright: smallest train/val accuracy gap
# (0.250 vs the unpruned default's 0.289), best macro F1 on BOTH the
# validation split (0.592 vs 0.550) and the harder Hussain edge-case real
# footage (0.511 vs 0.498), and a 72% smaller serialized model (7.8MB vs
# 27.7MB) -- not a trade-off, a strict improvement on every axis measured.
MIN_SAMPLES_LEAF = 20

# A follow-up 11-config sweep specifically targeting the REMAINING train/val
# gap (0.250 with min_samples_leaf=20 alone) tried max_features, max_samples
# (bootstrap subsample fraction), higher min_samples_leaf, and combinations.
# max_features=0.1 (each split only considers ~396 of the 3960 flattened
# features -- a much stronger decorrelation between trees than the sqrt(3960)
# ~= 63 features RandomForestClassifier's own default would pick) narrowed
# the validation-split gap further (0.250 -> 0.238) and, confirmed on real
# footage: cost ~1 point of accuracy on the easier Sanawar set (56.2% ->
# 55.2%) but gained ~8.7 points on the harder Hussain edge-case set (60.5% ->
# 69.2%) with better macro F1 there too (0.511 -> 0.565) -- fall-detection
# recall unchanged (100%/87.5%) on both sets. A real trade-off, not a free
# win, but this project has already concluded (docs/TCN_REGRESSION_REPORT.md)
# that the harder, more realistic Hussain set is the more decision-relevant
# one for the deployment recommendation, so this is kept as the default.
# max_samples=0.5 was also tried combined with this and closed the
# validation gap slightly further (0.218) but did worse on real footage
# (Hussain accuracy 68.6% vs 69.2%, more false alarms) -- not used.
#
# NOTE: MAX_FEATURES=0.1 (~396 of 3960 features per split) was tuned for
# the FLATTEN representation, which is what FEATURE_REPRESENTATION actually
# defaults to (see above) -- "summary" was investigated as a replacement
# default in docs/RF_GENERALIZATION_INVESTIGATION.md but was REJECTED after
# real-footage confirmation (it lost on the harder Hussain set), so it is
# kept only as an available, non-default option. SUMMARY_MAX_FEATURES="sqrt"
# is its own previously-tuned config, used only when a caller explicitly
# requests feature_representation="summary".
MAX_FEATURES = 0.1
SUMMARY_MAX_FEATURES = "sqrt"


def train(
    dataset_path: Path = LSTM_DATASET_NPZ,
    model_out: Path = RF_MODEL_PATH,
    encoder_out: Path = RF_ENCODER_PATH,
    val_split: float = 0.20,
    n_estimators: int = 300,
    max_depth: int = None,
    min_samples_leaf: int = MIN_SAMPLES_LEAF,
    max_features=None,
    feature_representation: str = FEATURE_REPRESENTATION,
    use_class_weights: bool = False,
):
    """
    Full training loop (same data/split/augmentation structure as
    tcn_trainer.train/lstm_trainer.train).

    use_class_weights (default False): kept off by default for the same
    evidence-based reason it was reverted for the TCN (see
    docs/TCN_IMPLEMENTATION_NOTES.md Phase 2.5) -- "balanced" weighting was shown
    there to trade a large amount of majority-class (Lying-heavy real
    footage) accuracy for minority-class recall, which is not a good
    default when it hasn't been validated for this model too. The
    parameter is exposed so it can be tried and measured, not applied
    blindly.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import StratifiedGroupKFold
        from sklearn.metrics import classification_report
        from sklearn.utils.class_weight import compute_class_weight
        import joblib
    except ImportError as e:
        raise ImportError(f"Missing dependency: {e}\nInstall with: pip install scikit-learn joblib\n")

    # ── Load dataset (identical to tcn_trainer.py) ────────────────────────────
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}.")
        print("Building dataset first...")
        from src.posture.lstm.lstm_dataset import build_dataset
        build_dataset()

    print(f"Loading dataset from {dataset_path}...")
    data = np.load(str(dataset_path), allow_pickle=True)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int32)
    groups = data["groups"]
    classes = data["classes"]
    col_medians = data["col_medians"].astype(np.float32) if "col_medians" in data else None

    print(f"  Dataset shape : X={X.shape}, y={y.shape}, groups={groups.shape}")
    print(f"  Classes       : {list(classes)}")
    # `col_medians` loaded above is a whole-REAL-dataset DIAGNOSTIC value only
    # (see lstm_dataset.py's build_dataset() "LEAKAGE FIX" comment) -- it must
    # NOT be used to impute this trainer's train/val folds, since it was
    # computed over validation-fold windows too. Deliberately not reused below.

    window_size = X.shape[1]
    n_features = X.shape[2]
    n_classes = len(classes)

    # ── Strict grouped split on REAL data only (same seed/scheme as TCN/LSTM) ──
    n_splits = max(2, round(1.0 / val_split))
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X, y, groups))

    X_val, y_val = X[val_idx], y[val_idx]
    X_train, y_train = X[train_idx], y[train_idx]

    # ── LEAKAGE FIX (this audit session, mirrors lstm_trainer.py exactly): impute
    # real train/val NaNs using medians computed from the TRAINING FOLD ONLY,
    # after the split above, BEFORE flattening/summarizing -- a RandomForest
    # cannot accept NaN input at all (sklearn raises), so without this fix
    # training would hard-fail (not just leak) the moment the npz was rebuilt
    # with lstm_dataset.py's raw-X leakage fix. See lstm_trainer.py's identical
    # comment for the full trace.
    from src.posture.lstm import lstm_features as lf
    train_col_medians = lf.compute_col_medians(X_train)
    X_train = lf.impute_nan(X_train, train_col_medians)
    X_val = lf.impute_nan(X_val, train_col_medians)

    # ── Post-split synthetic injection (train fold only, same as TCN/LSTM) ─────
    from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan
    print("  Generating synthetic windows for training fold...")
    X_syn, y_syn, _ = generate_synthetic_windows(window_size=window_size, n_per_class=800)
    X_syn = impute_nan(X_syn.astype(np.float32))
    X_train = np.concatenate([X_train, X_syn], axis=0).astype(np.float32)
    y_train = np.concatenate([y_train, y_syn], axis=0).astype(np.int32)
    rng = np.random.default_rng(seed=1)
    shuf = rng.permutation(len(X_train))
    X_train, y_train = X_train[shuf], y_train[shuf]

    print(f"\n  Train windows : {len(X_train)}  (real + synthetic)")
    print(f"  Val windows   : {len(X_val)}   (real ONLY)\n")

    print("  Train Balance (Windows):")
    for i, cls in enumerate(classes):
        mask = (y_train == i)
        print(f"    {cls:<10}: {mask.sum():>6} windows")

    # ── Reduce (N, window_size, n_features) to one feature vector per window ──
    if feature_representation not in FEATURE_REPRESENTATIONS:
        raise ValueError(f"feature_representation must be one of {list(FEATURE_REPRESENTATIONS)}, got {feature_representation!r}")
    represent_fn = FEATURE_REPRESENTATIONS[feature_representation]
    X_train_flat = represent_fn(X_train)
    X_val_flat = represent_fn(X_val)
    if max_features is None:
        max_features = SUMMARY_MAX_FEATURES if feature_representation == "summary" else MAX_FEATURES
    print(f"\n  Feature representation: {feature_representation!r} -> dim {X_train_flat.shape[1]}"
          f" (raw window was {window_size} x {n_features})")

    class_weight_param = None
    if use_class_weights:
        weights = compute_class_weight(class_weight="balanced", classes=np.arange(n_classes), y=y_train)
        class_weight_param = {i: float(w) for i, w in enumerate(weights)}
        print("\n  Class weights (balanced):")
        for i, cls in enumerate(classes):
            print(f"    {cls:<10}: {class_weight_param[i]:.3f}")

    # ── Train ─────────────────────────────────────────────────────────────────
    print(f"\nTraining RandomForestClassifier (n_estimators={n_estimators}, max_depth={max_depth}, "
          f"min_samples_leaf={min_samples_leaf}, max_features={max_features})...")
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        class_weight=class_weight_param,
        n_jobs=-1,
        random_state=42,
    )
    model.fit(X_train_flat, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    train_acc = model.score(X_train_flat, y_train)
    val_acc = model.score(X_val_flat, y_val)
    print(f"\nTrain accuracy      : {train_acc * 100:.2f}%")
    print(f"Validation accuracy : {val_acc * 100:.2f}%")

    y_pred = model.predict(X_val_flat)
    print("\nPer-class report:")
    print(classification_report(y_val, y_pred, target_names=list(classes), zero_division=0))

    # ── Save model ────────────────────────────────────────────────────────────
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, str(model_out))
    print(f"Model saved -> {model_out}")

    # ── Save label encoder (same shape as tcn/lstm's, so the same
    # SequenceWindowClassifier-style feature-building code can be reused
    # unmodified at inference time) ────────────────────────────────────────────
    # LEAKAGE FIX: train_col_medians (training fold only), not the
    # whole-dataset diagnostic `col_medians` loaded from the npz.
    encoder = {
        "classes": list(classes),
        "class_to_idx": {c: int(i) for i, c in enumerate(classes)},
        "window_size": int(window_size),
        "n_features": int(n_features),
        "col_medians": train_col_medians.tolist(),
        # RF-specific: which window->vector reduction this checkpoint expects
        # at inference time (rf_classifier.py reads this, not a hardcoded
        # assumption, so old "flatten" checkpoints stay loadable too).
        "feature_representation": feature_representation,
        "n_features_out": int(X_train_flat.shape[1]),
    }
    encoder_out.parent.mkdir(parents=True, exist_ok=True)
    encoder_out.write_text(json.dumps(encoder, indent=2), encoding="utf-8")
    print(f"Label encoder saved -> {encoder_out}")

    return model


def main():
    parser = argparse.ArgumentParser(description="Random Forest Posture Model Trainer")
    parser.add_argument("--n-estimators", type=int, default=300, help="Number of trees (default: 300)")
    parser.add_argument("--max-depth", type=int, default=None, help="Max tree depth (default: None = unbounded)")
    parser.add_argument("--val-split", type=float, default=0.20, help="Validation split ratio (default: 0.20)")
    parser.add_argument("--dataset", type=str, default=str(LSTM_DATASET_NPZ), help="Path to lstm_dataset.npz")
    parser.add_argument("--model-out", type=str, default=str(RF_MODEL_PATH), help="Output model path")
    parser.add_argument("--feature-representation", type=str, default=FEATURE_REPRESENTATION,
                         choices=list(FEATURE_REPRESENTATIONS), help="Window->vector reduction (default: flatten)")
    args = parser.parse_args()

    train(
        dataset_path=Path(args.dataset),
        model_out=Path(args.model_out),
        val_split=args.val_split,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        feature_representation=args.feature_representation,
    )


if __name__ == "__main__":
    main()
