"""Upload workflow step functions.

Each function represents one step in the upload workflow. They are
granular and map to a success-state in the handler so the handler can
emit corresponding WebSocket messages.

Functions here do not send WebSocket messages; they perform work and
return results or raise on fatal errors. Message sending stays in
`handler.py` as requested.
"""

from typing import Any, Dict, Optional, Tuple
import json
import httpx
from io import BytesIO
from app.config import (
    STORAGE_SERVICE_URL,
    VISION_SERVICE_URL,
    FILES_API_PREFIX,
    REPORTS_API_PREFIX,
)


async def receive_metadata(websocket) -> Dict[str, Any]:
    """Receive and parse the metadata JSON from the websocket.

    Returns the parsed metadata dict. Raises json.JSONDecodeError if parsing fails.
    """
    metadata_json = await websocket.receive_text()
    metadata = json.loads(metadata_json)
    return metadata


async def create_staging_report() -> str:
    """Create a staging report at the storage service and return report_id.

    Raises Exception on failure.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{STORAGE_SERVICE_URL}{REPORTS_API_PREFIX}", timeout=10.0
        )
        if resp.status_code != 200:
            raise Exception(f"Failed to create report on storage service: {resp.text}")
        resp_json = resp.json()

    upload_id = resp_json.get("report_id")
    if not upload_id:
        raise Exception(f"Storage service did not return report_id: {resp.text}")
    return upload_id


async def upload_report_image(
    upload_id: str, filename: str, file_data: bytes, content_type: str
) -> Dict[str, Any]:
    """Upload the main report image and return the storage service response JSON.

    Raises Exception on failure.
    """
    files = {"file": (filename, BytesIO(file_data), content_type)}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STORAGE_SERVICE_URL}{FILES_API_PREFIX}/upload/{upload_id}/report",
            files=files,
            timeout=30.0,
        )
        if response.status_code != 200:
            raise Exception(f"Failed to save file to storage service: {response.text}")
        return response.json()


async def send_to_vision_service(
    filename: str, file_data: bytes, content_type: str
) -> Dict[str, Any]:
    """Send image to the vision service and return its JSON response.

    This function returns the parsed JSON regardless of status code; the
    handler should inspect and decide how to proceed.
    """
    files = {"file": (filename, BytesIO(file_data), content_type)}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VISION_SERVICE_URL}/api/predict", files=files, timeout=30.0
        )
        return response.json()


async def upload_mask(upload_id: str, mask_bytes: bytes) -> Optional[Dict[str, Any]]:
    """Upload a segmentation mask to the storage service.

    Returns parsed JSON on success, or None on failure (mask saving is non-fatal).
    """
    files = {"file": ("mask.png", BytesIO(mask_bytes), "image/png")}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{STORAGE_SERVICE_URL}{FILES_API_PREFIX}/upload/{upload_id}/mask",
            files=files,
            timeout=30.0,
        )
        if response.status_code != 200:
            return None
        return response.json()
