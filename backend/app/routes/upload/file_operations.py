"""File operations for upload handling"""

import os
import uuid
from typing import Tuple
from ...config import UPLOAD_DIR


def generate_file_path(filename: str) -> Tuple[str, str, str]:
    """
    Generate unique file path and metadata for upload

    Returns:
        Tuple of (upload_id, file_path, file_url)
    """
    upload_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{upload_id}_{filename}")
    file_url = f"/files/{upload_id}_{filename}"

    return upload_id, file_path, file_url


def save_file(file_path: str, file_data: bytes) -> None:
    """
    Save binary data to file

    Args:
        file_path: Path where file should be saved
        file_data: Binary file data
    """
    with open(file_path, "wb") as f:
        f.write(file_data)


def save_mask(upload_id: str, mask_data: bytes) -> str:
    """
    Save segmentation mask to file

    Args:
        upload_id: Upload identifier
        mask_data: Binary PNG mask data

    Returns:
        Path where mask was saved
    """
    mask_path = os.path.join(UPLOAD_DIR, f"{upload_id}_mask.png")
    with open(mask_path, "wb") as f:
        f.write(mask_data)
    return mask_path


def calculate_progress(received_size: int, file_size: int) -> int:
    """
    Calculate upload progress percentage

    Args:
        received_size: Bytes received
        file_size: Total file size

    Returns:
        Progress percentage (0-100)
    """
    if file_size == 0:
        return 100
    return int((received_size / file_size) * 100)
