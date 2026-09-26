"""
Flower Classification - Model Training Script
------------------------------------------------
Trains an image classifier on the "tf_flowers" dataset
(5 classes: daisy, dandelion, roses, sunflowers, tulips)
using transfer learning on top of MobileNetV2.

Run:
    pip install -r requirements.txt
    python train_model.py

Outputs:
    flower_model.h5      -> the trained Keras model
    class_names.json     -> list of class labels, in the order the model predicts them
"""

import json
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from tensorflow.keras import layers, models

IMG_SIZE = 160
BATCH_SIZE = 32
EPOCHS_HEAD = 8          # training just the new classifier head
EPOCHS_FINE_TUNE = 6     # fine-tuning the top of the base model
LEARNING_RATE = 1e-3
FINE_TUNE_LR = 1e-5


def load_data():
    """Loads the tf_flowers dataset (downloaded automatically) and splits it
    into train / validation / test sets."""
    (train_ds, val_ds, test_ds), ds_info = tfds.load(
        "tf_flowers",
        split=["train[:80%]", "train[80%:90%]", "train[90%:]"],
        with_info=True,
        as_supervised=True,
    )
    class_names = ds_info.features["label"].names
    return train_ds, val_ds, test_ds, class_names


def preprocess(image, label):
    image = tf.image.resize(image, (IMG_SIZE, IMG_SIZE))
    image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
    return image, label


def prepare(ds, shuffle=False, augment=False):
    ds = ds.map(preprocess, num_parallel_calls=tf.data.AUTOTUNE)

    if augment:
        data_augmentation = tf.keras.Sequential([
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.15),
            layers.RandomZoom(0.15),
            layers.RandomContrast(0.1),
        ])
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y),
                    num_parallel_calls=tf.data.AUTOTUNE)

    if shuffle:
        ds = ds.shuffle(1000)

    return ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)


def build_model(num_classes):
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False

    inputs = tf.keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs)
    return model, base_model


def main():
    print("Loading data...")
    train_ds, val_ds, test_ds, class_names = load_data()
    num_classes = len(class_names)
    print(f"Classes ({num_classes}): {class_names}")

    train_ds = prepare(train_ds, shuffle=True, augment=True)
    val_ds = prepare(val_ds)
    test_ds = prepare(test_ds)

    model, base_model = build_model(num_classes)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    print("\n--- Stage 1: training classifier head ---")
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_HEAD)

    print("\n--- Stage 2: fine-tuning top layers of base model ---")
    base_model.trainable = True
    # Freeze everything except the last ~30 layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=FINE_TUNE_LR),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS_FINE_TUNE)

    print("\n--- Evaluating on test set ---")
    test_loss, test_acc = model.evaluate(test_ds)
    print(f"Test accuracy: {test_acc:.4f}")

    print("\nSaving model to flower_model.h5 ...")
    model.save("flower_model.h5")

    with open("class_names.json", "w") as f:
        json.dump(class_names, f)

    print("Done! Copy flower_model.h5 and class_names.json into the backend/ folder.")


if __name__ == "__main__":
    main()
