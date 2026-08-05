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
src/posture/lstm/lstm_features.py) is flattened into a single
(window_size * 132,) feature vector before fitting.

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


def train(
    dataset_path: Path = LSTM_DATASET_NPZ,
    model_out: Path = RF_MODEL_PATH,
    encoder_out: Path = RF_ENCODER_PATH,
    val_split: float = 0.20,
    n_estimators: int = 300,
    max_depth: int = None,
    min_samples_leaf: int = 2,
    use_class_weights: bool = False,
):
    """
    Full training loop (same data/split/augmentation structure as
    tcn_trainer.train/lstm_trainer.train).

    use_class_weights (default False): kept off by default for the same
    evidence-based reason it was reverted for the TCN (see
    TCN_IMPLEMENTATION_NOTES.md Phase 2.5) -- "balanced" weighting was shown
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

    window_size = X.shape[1]
    n_features = X.shape[2]
    n_classes = len(classes)

    # ── Strict grouped split on REAL data only (same seed/scheme as TCN/LSTM) ──
    n_splits = max(2, round(1.0 / val_split))
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X, y, groups))

    X_val, y_val = X[val_idx], y[val_idx]
    X_train, y_train = X[train_idx], y[train_idx]

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

    # ── Flatten (N, window_size, n_features) -> (N, window_size * n_features) ─
    X_train_flat = flatten_windows(X_train)
    X_val_flat = flatten_windows(X_val)
    print(f"\n  Flattened feature dim: {X_train_flat.shape[1]} (= {window_size} x {n_features})")

    class_weight_param = None
    if use_class_weights:
        weights = compute_class_weight(class_weight="balanced", classes=np.arange(n_classes), y=y_train)
        class_weight_param = {i: float(w) for i, w in enumerate(weights)}
        print("\n  Class weights (balanced):")
        for i, cls in enumerate(classes):
            print(f"    {cls:<10}: {class_weight_param[i]:.3f}")

    # ── Train ─────────────────────────────────────────────────────────────────
    print(f"\nTraining RandomForestClassifier (n_estimators={n_estimators}, max_depth={max_depth})...")
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
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
    encoder = {
        "classes": list(classes),
        "class_to_idx": {c: int(i) for i, c in enumerate(classes)},
        "window_size": int(window_size),
        "n_features": int(n_features),
        "col_medians": col_medians.tolist() if col_medians is not None else None,
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
    args = parser.parse_args()

    train(
        dataset_path=Path(args.dataset),
        model_out=Path(args.model_out),
        val_split=args.val_split,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
    )


if __name__ == "__main__":
    main()
