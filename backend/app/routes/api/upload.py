from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid
import os
from datetime import datetime
from ...config import UPLOAD_DIR

router = APIRouter()


@router.websocket("/api/upload/ws")
async def websocket_upload(websocket: WebSocket):
    """
    Handle WebSocket connection for file uploads with progress tracking.
    """
    await websocket.accept()
    print("WebSocket connection established")

    # Send connection status to client
    await websocket.send_json({"type": "status", "message": "Server connected"})

    try:
        # Wait for metadata message
        metadata_json = await websocket.receive_text()
        metadata = json.loads(metadata_json)
        print(f"Received file metadata: {metadata}")

        # Send metadata received confirmation
        await websocket.send_json(
            {
                "type": "status",
                "message": f"Received metadata for {metadata.get('filename', 'unknown file')}",
            }
        )

        if metadata.get("type") != "metadata":
            await websocket.send_json(
                {"type": "error", "error": "Expected metadata message first"}
            )
            return

        # Prepare for file data
        filename = metadata.get("filename", f"upload_{uuid.uuid4()}")
        file_size = metadata.get("size", 0)
        content_type = metadata.get("contentType", "application/octet-stream")

        # Generate a unique ID for this upload
        upload_id = str(uuid.uuid4())

        # File path for saving
        file_path = os.path.join(UPLOAD_DIR, f"{upload_id}_{filename}")

        # Notify client we're ready to receive file
        await websocket.send_json(
            {"type": "status", "message": f"Ready to receive file {filename}"}
        )

        # Receive binary data
        print(f"Waiting for file data for {filename}")
        file_data = await websocket.receive_bytes()

        # Notify client that file data is being processed
        await websocket.send_json({"type": "status", "message": "File uploading..."})

        # Calculate progress based on received vs expected size
        received_size = len(file_data)
        progress = int((received_size / file_size) * 100) if file_size > 0 else 100

        # Send progress update
        await websocket.send_json(
            {
                "type": "progress",
                "progress": progress,
                "received": received_size,
                "total": file_size,
                "message": f"Received {received_size} of {file_size} bytes ({progress}%)",
            }
        )

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_data)

        # Notify client that file has been saved
        await websocket.send_json(
            {"type": "status", "message": f"File saved successfully at {file_path}"}
        )

        # Create response data
        file_url = f"/files/{upload_id}_{filename}"  # URL where file can be accessed

        # Send success message
        await websocket.send_json(
            {
                "type": "success",
                "data": {
                    "id": upload_id,
                    "url": file_url,
                    "filename": filename,
                    "size": received_size,
                    "contentType": content_type,
                    "uploadedAt": datetime.now().isoformat(),
                    "status": "processed",
                },
                "message": "Upload complete and processed successfully",
            }
        )

        print(f"File saved successfully: {file_path}")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        # No need to send message as connection is already closed
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        await websocket.send_json(
            {"type": "error", "error": "Invalid JSON in metadata", "message": str(e)}
        )
    except Exception as e:
        print(f"Error during WebSocket upload: {e}")
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": str(e),
                    "message": f"Upload failed: {str(e)}",
                }
            )
        except:
            print("Failed to send error message, connection may be closed")
