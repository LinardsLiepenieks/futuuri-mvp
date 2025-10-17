"""Startup script - downloads data and trains model if needed"""

import os
import sys
import subprocess

MODEL_PATH = "/app/models/thyroid_unet_model.keras"


def check_and_train():
    """Check if model exists, train if not"""
    if os.path.exists(MODEL_PATH):
        print("✅ Model found, skipping training")
        return True

    print("⚠️  No model found!")
    print("🚀 Starting automatic training...")
    print("=" * 60)

    try:
        # Run training script
        result = subprocess.run(
            [sys.executable, "/app/train.py"],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        if os.path.exists(MODEL_PATH):
            print("=" * 60)
            print("✅ Training completed successfully!")
            return True
        else:
            print("❌ Training completed but model file not found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Training failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during training: {e}")
        return False


if __name__ == "__main__":
    success = check_and_train()
    sys.exit(0 if success else 1)
