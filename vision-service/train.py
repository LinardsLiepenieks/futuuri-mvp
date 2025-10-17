"""Training script for thyroid segmentation model"""

import os
import sys
import numpy as np
import cv2
import subprocess
from app.model import build_unet_model
from app.preprocessing import preprocessImg, preprocessMask

# Paths
DATA_DIR = "/app/data"
MODEL_PATH = "/app/models/thyroid_unet_model.keras"
DATASET_NAME = "tjahan/tn3k-thyroid-nodule-region-segmentation-dataset"


def download_dataset():
    """Download dataset from Kaggle if not already present"""
    if os.path.exists(f"{DATA_DIR}/trainval-image") and os.path.exists(
        f"{DATA_DIR}/trainval-mask"
    ):
        print("✅ Dataset already exists, skipping download")
        return

    print("📥 Downloading dataset from Kaggle...")
    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                DATASET_NAME,
                "-p",
                DATA_DIR,
                "--unzip",
            ],
            check=True,
        )
        print("✅ Dataset downloaded successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error downloading dataset: {e}")
        print("Make sure kaggle.json is properly mounted")
        sys.exit(1)


def load_images_and_masks():
    """Load all images and masks from dataset"""
    print("📂 Loading images and masks...")

    image_folder = f"{DATA_DIR}/trainval-image"
    mask_folder = f"{DATA_DIR}/trainval-mask"

    if not os.path.exists(image_folder) or not os.path.exists(mask_folder):
        raise FileNotFoundError(
            "Dataset folders not found. Run download_dataset() first."
        )

    image_files = sorted(os.listdir(image_folder))
    mask_files = sorted(os.listdir(mask_folder))

    images = []
    masks = []

    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        img = cv2.imread(img_path)[:, :, 0]
        images.append(img)

    for mask_file in mask_files:
        mask_path = os.path.join(mask_folder, mask_file)
        mask = cv2.imread(mask_path)[:, :, 0]
        mask = np.array(mask > 0.5, dtype=np.uint8)
        masks.append(mask)

    print(f"✅ Loaded {len(images)} images and {len(masks)} masks")
    return images, masks


def prepare_training_data(images, masks, test_fold=2):
    """
    Prepare training and test data using 5-fold cross-validation

    Args:
        images: List of image arrays
        masks: List of mask arrays
        test_fold: Which fold to use as test set (0-4)
    """
    print(f"🔄 Preparing data (test fold: {test_fold})...")

    x_train = []
    y_train = []
    x_test = []
    y_test = []

    for i in range(len(images)):
        if i % 5 == test_fold:
            x_test.append(preprocessImg(images[i]))
            y_test.append(preprocessMask(masks[i]))
        else:
            x_train.append(preprocessImg(images[i]))
            y_train.append(preprocessMask(masks[i]))

    x_train = np.array(x_train, dtype="float32")  # Changed from float16
    y_train = np.array(y_train, dtype="float32")  # Changed from uint8
    x_test = np.array(x_test, dtype="float32")  # Changed from float16
    y_test = np.array(y_test, dtype="float32")  # Changed from uint8

    # Add channel dimension
    x_train = x_train[..., np.newaxis]
    y_train = y_train[..., np.newaxis]
    x_test = x_test[..., np.newaxis]
    y_test = y_test[..., np.newaxis]

    print(f"   Train: {x_train.shape}, Test: {x_test.shape}")
    return x_train, y_train, x_test, y_test


def train_model(x_train, y_train, x_test, y_test, epochs=120):
    """Train the U-Net model"""
    print(f"🚀 Starting training for {epochs} epochs...")

    model = build_unet_model()

    history = model.fit(
        x=x_train,
        y=y_train,
        validation_data=(x_test, y_test),
        epochs=epochs,
        batch_size=16,
        shuffle=True,
        verbose=1,
    )

    return model, history


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("THYROID SEGMENTATION MODEL TRAINING")
    print("=" * 60)

    # Step 1: Download dataset
    download_dataset()

    # Step 2: Load data
    images, masks = load_images_and_masks()

    # Step 3: Prepare training data
    x_train, y_train, x_test, y_test = prepare_training_data(images, masks)

    # Step 4: Train model
    model, history = train_model(x_train, y_train, x_test, y_test, epochs=120)

    # Step 5: Save model
    print(f"💾 Saving model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH, include_optimizer=True)
    print("✅ Model saved successfully!")

    # Step 6: Evaluate
    print("\n📊 Final Evaluation:")
    loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
    print(f"   Test Loss: {loss:.4f}")
    print(f"   Test Accuracy: {accuracy:.4f}")

    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print(f"\nModel saved at: {MODEL_PATH}")
    print("You can now restart the API service to use the trained model.")


if __name__ == "__main__":
    main()
