"""Prediction endpoint for thyroid segmentation"""

from fastapi import APIRouter, File, UploadFile, HTTPException
import numpy as np
import cv2
import base64
from io import BytesIO
from ..preprocessing import prepare_image_for_prediction

router = APIRouter()

# Global variable to hold the model (loaded on startup)
model = None


def set_model(loaded_model):
    """Set the global model instance"""
    global model
    model = loaded_model


@router.post("/predict")
async def predict_segmentation(file: UploadFile = File(...)):
    """
    Predict thyroid nodule segmentation from uploaded image

    Args:
        file: Uploaded image file

    Returns:
        JSON with segmentation mask and metadata
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Read image bytes
        image_bytes = await file.read()

        # Log receipt
        print(f"Received image: {file.filename}, size: {len(image_bytes)} bytes")

        # Preprocess image
        processed_image = prepare_image_for_prediction(image_bytes)

        # Run prediction
        prediction = model.predict(processed_image, verbose=0)

        # Get the mask (remove batch and channel dimensions)
        mask = prediction[0, :, :, 0]

        # Apply threshold to get binary mask
        threshold = 0.5
        binary_mask = (mask > threshold).astype(np.uint8) * 255

        # Encode mask as base64 for transmission
        _, buffer = cv2.imencode(".png", binary_mask)
        mask_base64 = base64.b64encode(buffer).decode("utf-8")

        # Calculate some basic statistics
        segmented_area = np.sum(mask > threshold)
        total_area = mask.shape[0] * mask.shape[1]
        coverage_percent = (segmented_area / total_area) * 100

        return {
            "success": True,
            "filename": file.filename,
            "mask_base64": mask_base64,
            "statistics": {
                "segmented_pixels": int(segmented_area),
                "total_pixels": int(total_area),
                "coverage_percent": round(coverage_percent, 2),
                "threshold_used": threshold,
            },
        }

    except Exception as e:
        print(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if model is loaded and service is ready"""
    return {
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_loaded": model is not None,
    }
