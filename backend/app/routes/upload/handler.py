"""Upload workflow WebSocket handler kept deliberately high-level.

This module delegates detailed operations to `upload_steps` and `file_operations`.
The goal is to keep the handler easy to read top-to-bottom and focus on message
flow and error handling.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import uuid
from . import messages
from . import file_operations
from . import upload_steps
import httpx

router = APIRouter()


@router.websocket("/api/upload/ws")
async def websocket_upload(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established", flush=True)

    # Send connection status to client
    await websocket.send_json(messages.connection_message())

    try:
        # 1) Receive metadata
        metadata = await upload_steps.receive_metadata(websocket)
        print(f"Received file metadata: {metadata}", flush=True)

        filename = metadata.get("filename", f"upload_{uuid.uuid4()}")
        await websocket.send_json(messages.metadata_received_message(filename))

        if metadata.get("type") != "metadata":
            await websocket.send_json(messages.metadata_error_message())
            return

        file_size = metadata.get("size", 0)
        content_type = metadata.get("contentType", "application/octet-stream")

        if not content_type.startswith("image/"):
            await websocket.send_json(
                messages.generic_error_message("Only image files are supported")
            )
            return

        # 2) Create staging report
        await websocket.send_json(messages.creating_report_message())
        upload_id = await upload_steps.create_staging_report()
        file_url = f"/api/files/{upload_id}/report/{filename}"

        # 3) Receive file bytes
        await websocket.send_json(messages.ready_to_receive_message(filename))
        print(f"Waiting for file data for {filename}", flush=True)
        file_data = await websocket.receive_bytes()

        # 4) Progress update
        await websocket.send_json(messages.uploading_message())
        received_size = len(file_data)
        progress = file_operations.calculate_progress(received_size, file_size)
        await websocket.send_json(
            messages.progress_message(received_size, file_size, progress)
        )

        # 5) Upload report image
        await websocket.send_json(messages.sending_report_message())
        storage_result = await upload_steps.upload_report_image(
            upload_id, filename, file_data, content_type
        )
        await websocket.send_json(messages.file_saved_message(storage_result["path"]))
        print(f"File saved successfully: {storage_result['path']}", flush=True)

        # 6) Send to vision service
        await websocket.send_json(messages.vision_processing_message())
        vision_result = await upload_steps.send_to_vision_service(
            filename, file_data, content_type
        )
        print(f"Vision model response: {vision_result}", flush=True)

        # 7) Upload mask (if produced)
        if vision_result.get("success") and vision_result.get("mask_base64"):
            import base64

            mask_data = base64.b64decode(vision_result["mask_base64"])
            await websocket.send_json(messages.sending_mask_message())
            mask_result = await upload_steps.upload_mask(upload_id, mask_data)
            if mask_result:
                print(f"Saved mask to: {mask_result['path']}", flush=True)

        # Final success message
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
        except Exception:
            print("Failed to send error message, connection may be closed", flush=True)
