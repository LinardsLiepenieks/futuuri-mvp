"""WebSocket message models for upload responses"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """WebSocket message types"""

    STATUS = "status"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"


class BaseMessage(BaseModel):
    """Base message with type and message text"""

    type: MessageType
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for WebSocket JSON serialization"""
        return self.model_dump(mode="json")


class StatusMessage(BaseMessage):
    """Status update message"""

    type: MessageType = MessageType.STATUS


class ProgressMessage(BaseModel):
    """Progress update with percentage and byte counts"""

    type: MessageType = MessageType.PROGRESS
    progress: int = Field(..., ge=0, le=100, description="Progress percentage 0-100")
    received: int = Field(..., ge=0, description="Bytes received")
    total: int = Field(..., ge=0, description="Total bytes")
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class UploadData(BaseModel):
    """Upload success data"""

    id: str = Field(..., description="Upload/Report ID")
    url: str = Field(..., description="File URL")
    filename: str
    size: int = Field(..., ge=0)
    contentType: str
    uploadedAt: str = Field(..., description="ISO timestamp")
    status: str = Field(default="processed")
    visionResult: Optional[Dict[str, Any]] = None


class SuccessMessage(BaseModel):
    """Success message with upload data"""

    type: MessageType = MessageType.SUCCESS
    data: UploadData
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


class ErrorMessage(BaseModel):
    """Error message with error details"""

    type: MessageType = MessageType.ERROR
    error: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")


# Message builder functions (for backward compatibility and convenience)


def connection_message() -> Dict[str, Any]:
    """Initial connection status message"""
    return StatusMessage(message="Server connected").to_dict()


def metadata_received_message(filename: str) -> Dict[str, Any]:
    """Confirmation that metadata was received"""
    return StatusMessage(message=f"Received metadata for {filename}").to_dict()


def metadata_error_message() -> Dict[str, Any]:
    """Error when metadata is not sent first"""
    return ErrorMessage(
        error="Expected metadata message first",
        message="Expected metadata message first",
    ).to_dict()


def ready_to_receive_message(filename: str) -> Dict[str, Any]:
    """Notification that server is ready to receive file"""
    return StatusMessage(message=f"Ready to receive file {filename}").to_dict()


def uploading_message() -> Dict[str, Any]:
    """Message indicating file is being processed"""
    return StatusMessage(message="File uploading...").to_dict()


def progress_message(
    received_size: int, file_size: int, progress: int
) -> Dict[str, Any]:
    """Progress update message"""
    return ProgressMessage(
        progress=progress,
        received=received_size,
        total=file_size,
        message=f"Received {received_size} of {file_size} bytes ({progress}%)",
    ).to_dict()


def vision_processing_message() -> Dict[str, Any]:
    """Message indicating file is being sent to vision model"""
    return StatusMessage(message="Sending to vision model for processing...").to_dict()


def vision_success_message() -> Dict[str, Any]:
    """Message indicating vision processing completed successfully"""
    return StatusMessage(
        message="Vision model processing completed successfully"
    ).to_dict()


def sending_report_message() -> Dict[str, Any]:
    """Message indicating the report image is being sent to storage service"""
    return StatusMessage(message="Sending report image to storage service...").to_dict()


def sending_mask_message() -> Dict[str, Any]:
    """Message indicating the mask image is being sent to storage service"""
    return StatusMessage(
        message="Sending segmentation mask to storage service..."
    ).to_dict()


def file_saved_message(file_path: str) -> Dict[str, Any]:
    """Confirmation that file was saved"""
    return StatusMessage(message=f"File saved successfully at {file_path}").to_dict()


def creating_report_message() -> Dict[str, Any]:
    """Message indicating we're creating a report entry on the storage service"""
    return StatusMessage(message="Creating report on storage service...").to_dict()


def success_message(
    upload_id: str,
    file_url: str,
    filename: str,
    size: int,
    content_type: str,
) -> Dict[str, Any]:
    """Success response with file details"""
    return SuccessMessage(
        data=UploadData(
            id=upload_id,
            url=file_url,
            filename=filename,
            size=size,
            contentType=content_type,
            uploadedAt=datetime.now().isoformat(),
            status="processed",
        ),
        message="Upload complete and processed successfully",
    ).to_dict()


def json_error_message(error: str) -> Dict[str, Any]:
    """Error message for JSON decode failures"""
    return ErrorMessage(error="Invalid JSON in metadata", message=error).to_dict()


def generic_error_message(error: str) -> Dict[str, Any]:
    """Generic error message"""
    return ErrorMessage(error=error, message=f"Upload failed: {error}").to_dict()
