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


def build_model(window_size: int, n_features: int, n_classes: int):
    """
    Construct the LSTM classifier.

    Architecture
    ────────────
    Input  (window_size, n_features)
    LSTM(64, return_sequences=True)  – captures short-term motion patterns
    Dropout(0.3)
    LSTM(32)                         – summarises the sequence
    Dropout(0.3)
    Dense(n_classes, softmax)        – class probabilities
    """
    try:
        import tensorflow as tf
        from tensorflow import keras
    except ImportError:
        raise ImportError(
            "TensorFlow is required for training. Install it with:\n"
            "    pip install tensorflow-cpu\n"
        )

    model = keras.Sequential(
        [
            keras.layers.Input(shape=(window_size, n_features)),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.3),
            keras.layers.LSTM(32),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(n_classes, activation="softmax"),
        ],
        name="lstm_posture_classifier",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
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
):
    """Full training loop."""
    try:
        import tensorflow as tf
        from tensorflow import keras
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import classification_report
    except ImportError as e:
        raise ImportError(
            f"Missing dependency: {e}\n"
            "Install with: pip install tensorflow-cpu scikit-learn\n"
        )

    # ── Load dataset ──────────────────────────────────────────────────────────
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}.")
        print("Building dataset first…")
        from src.posture.lstm.lstm_dataset import build_dataset
        build_dataset()

    print(f"Loading dataset from {dataset_path}…")
    data = np.load(str(dataset_path), allow_pickle=True)
    X = data["X"].astype(np.float32)   # (N, window_size, 66)
    y = data["y"].astype(np.int32)     # (N,)
    classes = data["classes"]          # ['Fall', 'Lying', 'Sitting', 'Standing']

    print(f"  Dataset shape : X={X.shape}, y={y.shape}")
    print(f"  Classes       : {list(classes)}")

    window_size = X.shape[1]
    n_features = X.shape[2]
    n_classes = len(classes)

    # ── Train / validation split ──────────────────────────────────────────────
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=val_split, random_state=42, stratify=y
    )
    print(f"  Train samples : {len(X_train)}")
    print(f"  Val samples   : {len(X_val)}")

    # ── Build model ───────────────────────────────────────────────────────────
    model = build_model(window_size, n_features, n_classes)
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
    print(f"Model saved → {model_out}")

    # ── Save label encoder ────────────────────────────────────────────────────
    encoder = {
        "classes": list(classes),
        "class_to_idx": {c: int(i) for i, c in enumerate(classes)},
        "window_size": int(window_size),
        "n_features": int(n_features),
    }
    encoder_out.parent.mkdir(parents=True, exist_ok=True)
    encoder_out.write_text(json.dumps(encoder, indent=2), encoding="utf-8")
    print(f"Label encoder saved → {encoder_out}")

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
