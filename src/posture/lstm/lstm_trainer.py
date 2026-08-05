"""
lstm_trainer.py
===============
Trains an LSTM model on the sliding-window pose keypoint dataset and saves it
to models/lstm_posture.keras.

Usage:
    python src/posture/lstm/lstm_trainer.py [--epochs 100] [--batch-size 64]
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
LSTM_MODEL_PATH = MODELS_DIR / "lstm_posture.keras"
LSTM_ENCODER_PATH = MODELS_DIR / "lstm_label_encoder.json"


def build_model(
    window_size: int,
    n_features: int,
    n_classes: int,
    units1: int = 64,
    units2: int = 32,
    dropout_rate: float = 0.3,
    learning_rate: float = 1e-3,
    l1: float = 0.0,
    l2: float = 0.0,
):
    """
    Construct the LSTM classifier.

    Architecture
    ────────────
    Input  (window_size, n_features)
    LSTM(units1, return_sequences=True)  – captures short-term motion patterns
    Dropout(dropout_rate)
    LSTM(units2)                         – summarises the sequence
    Dropout(dropout_rate)
    Dense(n_classes, softmax)            – class probabilities

    units1/units2/dropout_rate/learning_rate default to the original fixed
    values (64, 32, 0.3, 1e-3) so existing callers see no behavior change;
    they're exposed as parameters purely for hyperparameter sweeps (see
    compare_tcn_lstm.py's optimization pass).

    l1/l2 add an L1/L2 weight-magnitude penalty (kernel_regularizer, plus
    recurrent_regularizer on the LSTM layers since their recurrent weights
    can overfit the same way) on top of the existing Dropout. Both default
    to 0.0, which produces no regularizer object at all (not just a
    zero-coefficient one) so existing callers see byte-identical model
    graphs. Motivated by a visible train/val accuracy gap (~90%+ train vs
    ~65-70% val) suggestive of some overfitting -- see TCN_IMPLEMENTATION_NOTES.md.
    """
    try:
        import tensorflow as tf
        from tensorflow import keras
    except ImportError:
        raise ImportError(
            "TensorFlow is required for training. Install it with:\n"
            "    pip install tensorflow-cpu\n"
        )

    reg = keras.regularizers.l1_l2(l1=l1, l2=l2) if (l1 > 0 or l2 > 0) else None

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(window_size, n_features)),
            keras.layers.LSTM(
                units1, return_sequences=True,
                kernel_regularizer=reg, recurrent_regularizer=reg,
            ),
            keras.layers.Dropout(dropout_rate),
            keras.layers.LSTM(
                units2,
                kernel_regularizer=reg, recurrent_regularizer=reg,
            ),
            keras.layers.Dropout(dropout_rate),
            keras.layers.Dense(n_classes, activation="softmax", kernel_regularizer=reg),
        ],
        name="lstm_posture_classifier",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def train(
    dataset_path: Path = LSTM_DATASET_NPZ,
    model_out: Path = LSTM_MODEL_PATH,
    encoder_out: Path = LSTM_ENCODER_PATH,
    epochs: int = 100,
    batch_size: int = 64,
    val_split: float = 0.20,
    units1: int = 64,
    units2: int = 32,
    dropout_rate: float = 0.3,
    learning_rate: float = 1e-3,
    l1: float = 0.0,
    l2: float = 0.0,
    use_class_weights: bool = False,
):
    """
    Full training loop.

    use_class_weights (default False): weight each class's loss contribution
    by inverse frequency ("balanced" scheme). Exposed for parity with
    tcn_trainer.train()/rf_trainer.train(), which have the same parameter --
    kept off by default here too, since the TCN ablation (see
    TCN_IMPLEMENTATION_NOTES.md Phase 2.5) measured "balanced" weighting
    trading a large amount of majority-class (Lying-heavy real footage)
    accuracy for minority-class recall on that architecture; it has not
    been separately validated for the LSTM, so it isn't turned on by
    default here either without the same kind of before/after check.
    """
    try:
        import tensorflow as tf
        from tensorflow import keras
        from sklearn.model_selection import StratifiedGroupKFold
        from sklearn.metrics import classification_report
        from sklearn.utils.class_weight import compute_class_weight
    except ImportError as e:
        raise ImportError(
            f"Missing dependency: {e}\n"
            "Install with: pip install tensorflow-cpu scikit-learn\n"
        )

    # Fix the model's weight-initialization/dropout randomness so repeated
    # runs with the same hyperparameters are reproducible instead of landing
    # on a different local optimum each time -- otherwise architecture
    # comparisons (e.g. against the TCN) are confounded by training noise
    # rather than reflecting the hyperparameters actually being compared.
    keras.utils.set_random_seed(42)

    # ── Load dataset ──────────────────────────────────────────────────────────
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}.")
        print("Building dataset first…")
        from src.posture.lstm.lstm_dataset import build_dataset
        build_dataset()

    print(f"Loading dataset from {dataset_path}…")
    data = np.load(str(dataset_path), allow_pickle=True)
    X = data["X"].astype(np.float32)   # (N, window_size, 132)
    y = data["y"].astype(np.int32)     # (N,)
    groups = data["groups"]            # (N,)
    classes = data["classes"]          # ['Fall', 'Lying', 'Sitting', 'Standing', 'Unknown']
    col_medians = data["col_medians"].astype(np.float32) if "col_medians" in data else None

    print(f"  Dataset shape : X={X.shape}, y={y.shape}, groups={groups.shape}")
    print(f"  Classes       : {list(classes)}")

    window_size = X.shape[1]
    n_features = X.shape[2]
    n_classes = len(classes)

    # ── Strict grouped split on REAL data only ────────────────────────────────
    # n_splits derived from val_split (e.g. 0.20 -> 5 folds -> ~20% held out
    # as the validation fold) so the val_split parameter actually controls
    # the split instead of being silently ignored in favor of a hardcoded 5.
    n_splits = max(2, round(1.0 / val_split))
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X, y, groups))

    X_val,   y_val,   g_val   = X[val_idx],   y[val_idx],   groups[val_idx]
    X_train, y_train, g_train = X[train_idx], y[train_idx], groups[train_idx]

    # ── Post-split synthetic injection (train fold only) ──────────────────────
    from src.posture.lstm.lstm_dataset import generate_synthetic_windows, impute_nan
    print("  Generating synthetic windows for training fold...")
    X_syn, y_syn, _ = generate_synthetic_windows(window_size=window_size, n_per_class=800)
    X_syn = impute_nan(X_syn.astype(np.float32))
    X_train = np.concatenate([X_train, X_syn], axis=0).astype(np.float32)
    y_train = np.concatenate([y_train, y_syn], axis=0).astype(np.int32)
    # Re-shuffle augmented train fold
    rng = np.random.default_rng(seed=1)
    shuf = rng.permutation(len(X_train))
    X_train, y_train = X_train[shuf], y_train[shuf]

    print(f"\n  Split Results (val = 100% real, no synthetic):")
    print(f"  Train windows : {len(X_train)}  (real + synthetic)")
    print(f"  Val windows   : {len(X_val)}   (real ONLY)\n")

    print("  Train Balance (Windows):")
    for i, cls in enumerate(classes):
        mask = (y_train == i)
        print(f"    {cls:<10}: {mask.sum():>6} windows")

    # ── Class weights (balanced, computed from the actual train fold) ─────────
    class_weight_dict = None
    if use_class_weights:
        weights = compute_class_weight(class_weight="balanced", classes=np.arange(n_classes), y=y_train)
        class_weight_dict = {i: float(w) for i, w in enumerate(weights)}
        print("\n  Class weights (balanced):")
        for i, cls in enumerate(classes):
            print(f"    {cls:<10}: {class_weight_dict[i]:.3f}")

    print("\n  Val Balance (Windows / Unique Real Sequences):")
    for i, cls in enumerate(classes):
        mask = (y_val == i)
        n_seq = int(np.unique(g_val[mask]).shape[0]) if mask.sum() > 0 else 0
        print(f"    {cls:<10}: {mask.sum():>6} windows / {n_seq:>3} real sequences")


    # ── Build model ───────────────────────────────────────────────────────────
    model = build_model(
        window_size, n_features, n_classes,
        units1=units1, units2=units2, dropout_rate=dropout_rate, learning_rate=learning_rate,
        l1=l1, l2=l2,
    )
    model.summary()

    # ── Callbacks ─────────────────────────────────────────────────────────────
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=10,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            verbose=1,
        ),
    ]

    # ── Train ─────────────────────────────────────────────────────────────────
    print(f"\nTraining for up to {epochs} epochs (batch={batch_size})…")
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, y_val),
        callbacks=callbacks,
        class_weight=class_weight_dict,
        verbose=2,
    )

    # ── Evaluate ──────────────────────────────────────────────────────────────
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    print(f"\nValidation accuracy : {val_acc * 100:.2f}%")
    print(f"Validation loss     : {val_loss:.4f}")

    y_pred = np.argmax(model.predict(X_val, verbose=0), axis=1)
    print("\nPer-class report:")
    print(classification_report(y_val, y_pred, target_names=list(classes)))

    # ── Save model ────────────────────────────────────────────────────────────
    model_out.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_out))
    print(f"Model saved -> {model_out}")

    # ── Save label encoder ────────────────────────────────────────────────────
    # col_medians travels with the encoder so lstm_classifier.py imputes
    # missing landmarks at inference time with the SAME per-feature medians
    # used during training, instead of an arbitrary constant fill value.
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

    return model, history


def main():
    parser = argparse.ArgumentParser(description="LSTM Posture Model Trainer")
    parser.add_argument("--epochs", type=int, default=100, help="Max training epochs (default: 100)")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size (default: 64)")
    parser.add_argument("--val-split", type=float, default=0.20, help="Validation split ratio (default: 0.20)")
    parser.add_argument("--dataset", type=str, default=str(LSTM_DATASET_NPZ), help="Path to lstm_dataset.npz")
    parser.add_argument("--model-out", type=str, default=str(LSTM_MODEL_PATH), help="Output model path")
    args = parser.parse_args()

    train(
        dataset_path=Path(args.dataset),
        model_out=Path(args.model_out),
        epochs=args.epochs,
        batch_size=args.batch_size,
        val_split=args.val_split,
    )


if __name__ == "__main__":
    main()
