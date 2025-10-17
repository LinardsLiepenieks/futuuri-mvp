"""WebSocket upload handler"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid
from . import messages
from . import file_operations

router = APIRouter()


@router.websocket("/api/upload/ws")
async def websocket_upload(websocket: WebSocket):
    """
    Handle WebSocket connection for file uploads with progress tracking.
    """
    await websocket.accept()
    print("WebSocket connection established")

    # Send connection status to client
    await websocket.send_json(messages.connection_message())

    try:
        # Wait for metadata message
        metadata_json = await websocket.receive_text()
        metadata = json.loads(metadata_json)
        print(f"Received file metadata: {metadata}")

        # Send metadata received confirmation
        filename = metadata.get("filename", "unknown file")
        await websocket.send_json(messages.metadata_received_message(filename))

        if metadata.get("type") != "metadata":
            await websocket.send_json(messages.metadata_error_message())
            return

        # Prepare for file data
        filename = metadata.get("filename", f"upload_{uuid.uuid4()}")
        file_size = metadata.get("size", 0)
        content_type = metadata.get("contentType", "application/octet-stream")

        # Generate file paths
        upload_id, file_path, file_url = file_operations.generate_file_path(filename)

        # Notify client we're ready to receive file
        await websocket.send_json(messages.ready_to_receive_message(filename))

        # Receive binary data
        print(f"Waiting for file data for {filename}")
        file_data = await websocket.receive_bytes()

        # Notify client that file data is being processed
        await websocket.send_json(messages.uploading_message())

        # Calculate progress
        received_size = len(file_data)
        progress = file_operations.calculate_progress(received_size, file_size)

        # Send progress update
        await websocket.send_json(
            messages.progress_message(received_size, file_size, progress)
        )

        # Save file
        file_operations.save_file(file_path, file_data)

        # Notify client that file has been saved
        await websocket.send_json(messages.file_saved_message(file_path))

        # Send success message
        await websocket.send_json(
            messages.success_message(
                upload_id, file_url, filename, received_size, content_type
            )
        )

        print(f"File saved successfully: {file_path}")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        # No need to send message as connection is already closed
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        await websocket.send_json(messages.json_error_message(str(e)))
    except Exception as e:
        print(f"Error during WebSocket upload: {e}")
        try:
            await websocket.send_json(messages.generic_error_message(str(e)))
        except:
            print("Failed to send error message, connection may be closed")
