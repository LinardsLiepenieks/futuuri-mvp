"""U-Net model architecture and utilities"""

import tensorflow as tf
import os


def binary_focal_loss(gamma=2.0, alpha=0.25):
    """Binary Focal Loss function"""

    def focal_loss(y_true, y_pred):
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.keras.backend.clip(y_pred, epsilon, 1.0 - epsilon)
        cross_entropy = -y_true * tf.math.log(y_pred) - (1 - y_true) * tf.math.log(
            1 - y_pred
        )
        weight = alpha * tf.pow(1 - y_pred, gamma) * y_true + (1 - alpha) * tf.pow(
            y_pred, gamma
        ) * (1 - y_true)
        return tf.reduce_mean(weight * cross_entropy)

    return focal_loss


def build_unet_model():
    """
    Build U-Net model architecture for 128x128 thyroid segmentation

    Returns:
        Compiled Keras model
    """
    inputs = tf.keras.layers.Input(shape=(128, 128, 1))

    # Contraction path
    c1 = tf.keras.layers.Conv2D(
        16, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(inputs)
    c1 = tf.keras.layers.Dropout(0.1)(c1)
    c1 = tf.keras.layers.Conv2D(
        16, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c1)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)

    c2 = tf.keras.layers.Conv2D(
        32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(p1)
    c2 = tf.keras.layers.Dropout(0.1)(c2)
    c2 = tf.keras.layers.Conv2D(
        32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c2)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)

    c3 = tf.keras.layers.Conv2D(
        64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(p2)
    c3 = tf.keras.layers.Dropout(0.2)(c3)
    c3 = tf.keras.layers.Conv2D(
        64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c3)
    p3 = tf.keras.layers.MaxPooling2D((2, 2))(c3)

    c4 = tf.keras.layers.Conv2D(
        128, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(p3)
    c4 = tf.keras.layers.Dropout(0.2)(c4)
    c4 = tf.keras.layers.Conv2D(
        128, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c4)

    # Expansive path
    u7 = tf.keras.layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding="same")(c4)
    u7 = tf.keras.layers.concatenate([u7, c3])
    c7 = tf.keras.layers.Conv2D(
        64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(u7)
    c7 = tf.keras.layers.Dropout(0.1)(c7)
    c7 = tf.keras.layers.Conv2D(
        64, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c7)

    u8 = tf.keras.layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding="same")(c7)
    u8 = tf.keras.layers.concatenate([u8, c2])
    c8 = tf.keras.layers.Conv2D(
        32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(u8)
    c8 = tf.keras.layers.Dropout(0.1)(c8)
    c8 = tf.keras.layers.Conv2D(
        32, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c8)

    u9 = tf.keras.layers.Conv2DTranspose(16, (2, 2), strides=(2, 2), padding="same")(c8)
    u9 = tf.keras.layers.concatenate([u9, c1], axis=3)
    c9 = tf.keras.layers.Conv2D(
        16, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(u9)
    c9 = tf.keras.layers.Dropout(0.1)(c9)
    c9 = tf.keras.layers.Conv2D(
        16, (3, 3), activation="relu", kernel_initializer="he_normal", padding="same"
    )(c9)

    outputs = tf.keras.layers.Conv2D(1, (1, 1), activation="sigmoid")(c9)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    loss_fn = binary_focal_loss(gamma=2.0, alpha=0.25)
    model.compile(optimizer="adam", loss=loss_fn, metrics=["accuracy"])

    return model


def load_model(model_path="/app/models/thyroid_unet_model.keras"):
    """
    Load trained model from disk

    Args:
        model_path: Path to saved model file

    Returns:
        Loaded Keras model
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Please train the model first."
        )

    # Load with custom loss function
    custom_objects = {"focal_loss": binary_focal_loss(gamma=2.0, alpha=0.25)}
    model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)

    print(f"Model loaded successfully from {model_path}")
    return model
