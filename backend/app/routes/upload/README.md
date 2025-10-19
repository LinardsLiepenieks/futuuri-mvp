# Upload Route Documentation

## Structure

This package handles the WebSocket-based file upload workflow for medical images.

### Files

- **`handler.py`** - Main WebSocket endpoint handler for the upload workflow
- **`messages.py`** - Pydantic-based message models with type-safe serialization
- **`file_operations.py`** - File utility functions (progress calculation, etc.)
- **`file_operations.py`** - File utility functions (progress calculation, etc.)
- **`__init__.py`** - Package exports

## Message Types

All WebSocket messages use standardized Pydantic models with the `MessageType` enum:

### MessageType Enum

```python
class MessageType(str, Enum):
    STATUS = "status"
    PROGRESS = "progress"
    SUCCESS = "success"
    ERROR = "error"
```

### Message Models

#### StatusMessage

Used for general status updates throughout the workflow.

```python
{
    "type": "status",
    "message": "Server connected"
}
```

#### ProgressMessage

Upload progress with byte counts and percentage.

```python
{
    "type": "progress",
    "progress": 50,
    "received": 1024,
    "total": 2048,
    "message": "Received 1024 of 2048 bytes (50%)"
}
```

#### SuccessMessage

Final success response with upload data and vision results.

```python
{
    "type": "success",
    "data": {
        "id": "uuid",
        "url": "/api/files/...",
        "filename": "image.jpg",
        "size": 1024,
        "contentType": "image/jpeg",
        "uploadedAt": "2025-10-19T...",
        "status": "processed",
        "visionResult": {...}
    },
    "message": "Upload complete and processed successfully"
}
```

#### ErrorMessage

Error notifications with details.

```python
{
    "type": "error",
    "error": "Validation failed",
    "message": "Upload failed: Validation failed"
}
```

## Upload Workflow

1. **Connection** - Client connects to `/api/upload/ws`
2. **Metadata** - Client sends file metadata (filename, size, contentType)
3. **Create Report** - Backend creates staging report in storage service
4. **File Upload** - Client sends binary file data
5. **Storage** - Backend saves report image to storage service
6. **Vision Processing** - Backend sends image to vision service for segmentation
7. **Mask Storage** - Backend saves segmentation mask to storage service
8. **Success** - Backend sends final success message with all data

## Benefits of Pydantic Models

- **Type Safety** - IDE autocomplete and type checking
- **Validation** - Automatic validation of message structure
- **Documentation** - Self-documenting message schemas
- **Testing** - Easy to test and mock
- **Serialization** - Automatic JSON serialization with `mode='json'`

## Usage Example

```python
from app.routes.upload import messages

# Create and send a status message
status = messages.StatusMessage(message="Processing...")
await websocket.send_json(status.to_dict())

# Or use convenience functions (same result)
await websocket.send_json(messages.uploading_message())
```
