"""WebSocket upload handler"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid
import httpx
from . import messages
from . import file_operations

router = APIRouter()


@router.websocket("/api/upload/ws")
async def websocket_upload(websocket: WebSocket):
    """
    Handle WebSocket connection for file uploads with progress tracking.
    """
    await websocket.accept()
    print("WebSocket connection established", flush=True)

    # Send connection status to client
    await websocket.send_json(messages.connection_message())

    try:
        # Wait for metadata message
        metadata_json = await websocket.receive_text()
        metadata = json.loads(metadata_json)
        print(f"Received file metadata: {metadata}", flush=True)

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
        print(f"Waiting for file data for {filename}", flush=True)
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

        print(f"File saved successfully: {file_path}", flush=True)

        # Send to vision model for processing
        await websocket.send_json(messages.vision_processing_message())

        async with httpx.AsyncClient() as client:
            with open(file_path, "rb") as f:
                files = {"file": (filename, f, content_type)}
                response = await client.post(
                    "http://vision-service:8001/api/predict", files=files, timeout=30.0
                )
                vision_result = response.json()

        print(f"Vision model response: {vision_result}", flush=True)

        # Save the segmentation mask
        if vision_result.get("success") and vision_result.get("mask_base64"):
            import base64

            mask_data = base64.b64decode(vision_result["mask_base64"])
            mask_path = file_operations.save_mask(upload_id, mask_data)
            print(f"Saved mask to: {mask_path}", flush=True)

        # Send success message with vision result
        success_msg = messages.success_message(
            upload_id, file_url, filename, received_size, content_type
        )
        success_msg["data"]["visionResult"] = vision_result
        await websocket.send_json(success_msg)

    except WebSocketDisconnect:
        print("WebSocket disconnected", flush=True)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", flush=True)
        await websocket.send_json(messages.json_error_message(str(e)))
    except Exception as e:
        print(f"Error during WebSocket upload: {e}", flush=True)
        try:
            await websocket.send_json(messages.generic_error_message(str(e)))
        except:
            print("Failed to send error message, connection may be closed", flush=True)
