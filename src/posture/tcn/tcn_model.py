"""
tcn_model.py
============
Temporal Convolutional Network (TCN) architecture for posture classification.

Consumes exactly the same (window_size, 132) input as the LSTM
(lstm_features.FEATURE_DIM: normalized position + velocity, see
src/posture/lstm/lstm_features.py) so it can be trained on the same
data/lstm_dataset.npz and swapped in as a drop-in alternative to the LSTM.

Architecture
------------
A stack of residual blocks, each with two causal, dilated Conv1D layers.
Dilation rates 1, 2, 4, 8 give the last block a receptive field of
2*(1+2+4+8)+1 = 31 frames -- wide enough to cover the whole 30-frame window
by itself. Causal padding means the output at position t only ever depends
on inputs at positions <= t, matching the LSTM's left-to-right processing
order and keeping the model realtime-safe (no lookahead into future frames).

Each residual block:

    Conv1D(filters, kernel_size, dilation_rate, padding="causal")
    LayerNormalization -> ReLU -> Dropout
    Conv1D(filters, kernel_size, dilation_rate, padding="causal")
    LayerNormalization -> ReLU -> Dropout
    + residual connection (1x1 Conv1D projection when channel counts differ)

LayerNormalization (rather than BatchNormalization) is used because it
normalizes per-timestep-per-sample instead of across the batch, so its
behaviour at single-window inference time (batch size 1, see
tcn_classifier.py) exactly matches training instead of depending on batch
statistics collected during fitting.

GlobalAveragePooling1D collapses the (window_size, filters) block output to
a single (filters,) summary vector, then a Dense+softmax head produces the
same 5-class distribution as the LSTM (see lstm_dataset.CLASSES).
"""

DILATION_RATES = (1, 2, 4, 8)
NUM_FILTERS = 32
KERNEL_SIZE = 3
DROPOUT_RATE = 0.2


def _residual_block(x, filters: int, kernel_size: int, dilation_rate: int, dropout_rate: float, block_idx: int):
    from tensorflow import keras

    prev = x
    y = keras.layers.Conv1D(
        filters, kernel_size, padding="causal", dilation_rate=dilation_rate,
        name=f"tcn_block{block_idx}_conv1",
    )(x)
    y = keras.layers.LayerNormalization(name=f"tcn_block{block_idx}_norm1")(y)
    y = keras.layers.Activation("relu", name=f"tcn_block{block_idx}_relu1")(y)
    y = keras.layers.Dropout(dropout_rate, name=f"tcn_block{block_idx}_drop1")(y)

    y = keras.layers.Conv1D(
        filters, kernel_size, padding="causal", dilation_rate=dilation_rate,
        name=f"tcn_block{block_idx}_conv2",
    )(y)
    y = keras.layers.LayerNormalization(name=f"tcn_block{block_idx}_norm2")(y)
    y = keras.layers.Activation("relu", name=f"tcn_block{block_idx}_relu2")(y)
    y = keras.layers.Dropout(dropout_rate, name=f"tcn_block{block_idx}_drop2")(y)

    # Project the residual path when the block changed the channel count, so
    # the Add() below always sums matching shapes.
    if prev.shape[-1] != filters:
        prev = keras.layers.Conv1D(filters, 1, padding="same", name=f"tcn_block{block_idx}_proj")(prev)

    out = keras.layers.Add(name=f"tcn_block{block_idx}_add")([prev, y])
    return keras.layers.Activation("relu", name=f"tcn_block{block_idx}_out")(out)


def build_tcn_model(
    window_size: int,
    n_features: int,
    n_classes: int,
    num_filters: int = NUM_FILTERS,
    kernel_size: int = KERNEL_SIZE,
    dilation_rates=DILATION_RATES,
    dropout_rate: float = DROPOUT_RATE,
    learning_rate: float = 1e-3,
):
    """
    Construct the TCN posture classifier.

    Mirrors lstm_trainer.build_model's signature (window_size, n_features,
    n_classes) so tcn_trainer.py can call it as a drop-in replacement for the
    LSTM's build_model in an otherwise identical training loop.
    """
    try:
        from tensorflow import keras
    except ImportError:
        raise ImportError(
            "TensorFlow is required for training. Install it with:\n"
            "    pip install tensorflow-cpu\n"
        )

    inputs = keras.layers.Input(shape=(window_size, n_features), name="window_input")
    x = inputs
    for i, dilation_rate in enumerate(dilation_rates):
        x = _residual_block(x, num_filters, kernel_size, dilation_rate, dropout_rate, block_idx=i)

    x = keras.layers.GlobalAveragePooling1D(name="tcn_global_pool")(x)
    outputs = keras.layers.Dense(n_classes, activation="softmax", name="posture_output")(x)

    model = keras.Model(inputs, outputs, name="tcn_posture_classifier")
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model
