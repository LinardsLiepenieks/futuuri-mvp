"""Image preprocessing functions for U-Net segmentation"""

import numpy as np
import cv2


def preprocessImg(img):
    """
    Preprocessing images for the segmentation CNN

    Args:
        img: 2D numpy array (one image)

    Returns:
        Image scaled to 128x128 pixels with float16 values between 0 and 1
    """
    if np.max(img) > np.min(img):
        img = cv2.resize(img, (128, 128))
        img = (img - np.min(img)) / (np.max(img) - np.min(img))
    else:
        img = np.zeros((128, 128))
    return img.astype("float16")


def preprocessMask(mask):
    """
    Preprocessing masks for the segmentation CNN

    Args:
        mask: 2D numpy array (one segmentation mask)

    Returns:
        Mask scaled to 128x128 pixels and converted to binary
    """
    mask = cv2.resize(np.array(mask, dtype="uint8"), (128, 128))
    mask = np.array(mask > 0.5, dtype=int)
    return mask


def prepare_image_for_prediction(image_bytes):
    """
    Prepare uploaded image bytes for model prediction

    Args:
        image_bytes: Raw image bytes from upload

    Returns:
        Preprocessed image ready for model (128, 128, 1)
    """
    # Decode image from bytes
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    # Preprocess
    img = preprocessImg(img)

    # Add channel dimension
    img = img[..., np.newaxis]

    # Add batch dimension
    img = np.expand_dims(img, axis=0)

    return img
