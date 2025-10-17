"""WebSocket message builders for upload responses"""

from typing import Dict, Any
from datetime import datetime


def connection_message() -> Dict[str, str]:
    """Initial connection status message"""
    return {"type": "status", "message": "Server connected"}


def metadata_received_message(filename: str) -> Dict[str, str]:
    """Confirmation that metadata was received"""
    return {
        "type": "status",
        "message": f"Received metadata for {filename}",
    }


def metadata_error_message() -> Dict[str, str]:
    """Error when metadata is not sent first"""
    return {"type": "error", "error": "Expected metadata message first"}


def ready_to_receive_message(filename: str) -> Dict[str, str]:
    """Notification that server is ready to receive file"""
    return {"type": "status", "message": f"Ready to receive file {filename}"}


def uploading_message() -> Dict[str, str]:
    """Message indicating file is being processed"""
    return {"type": "status", "message": "File uploading..."}


def progress_message(
    received_size: int, file_size: int, progress: int
) -> Dict[str, Any]:
    """Progress update message"""
    return {
        "type": "progress",
        "progress": progress,
        "received": received_size,
        "total": file_size,
        "message": f"Received {received_size} of {file_size} bytes ({progress}%)",
    }


def file_saved_message(file_path: str) -> Dict[str, str]:
    """Confirmation that file was saved"""
    return {"type": "status", "message": f"File saved successfully at {file_path}"}


def success_message(
    upload_id: str,
    file_url: str,
    filename: str,
    size: int,
    content_type: str,
) -> Dict[str, Any]:
    """Success response with file details"""
    return {
        "type": "success",
        "data": {
            "id": upload_id,
            "url": file_url,
            "filename": filename,
            "size": size,
            "contentType": content_type,
            "uploadedAt": datetime.now().isoformat(),
            "status": "processed",
        },
        "message": "Upload complete and processed successfully",
    }


def json_error_message(error: str) -> Dict[str, str]:
    """Error message for JSON decode failures"""
    return {
        "type": "error",
        "error": "Invalid JSON in metadata",
        "message": error,
    }


def generic_error_message(error: str) -> Dict[str, str]:
    """Generic error message"""
    return {
        "type": "error",
        "error": error,
        "message": f"Upload failed: {error}",
    }
