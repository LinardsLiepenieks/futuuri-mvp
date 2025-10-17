"""Vision Service - Thyroid Segmentation API"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .model import load_model
from .routes import predict
import os

app = FastAPI(
    title="Thyroid Segmentation Vision Service",
    description="U-Net based thyroid nodule segmentation service",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load model on startup
@app.on_event("startup")
async def startup_event():
    """Load the trained model when service starts"""
    model_path = "/app/models/thyroid_unet_model.keras"

    try:
        if os.path.exists(model_path):
            model = load_model(model_path)
            predict.set_model(model)
            print("✅ Model loaded successfully")
        else:
            print(f"⚠️  Model not found at {model_path}")
            print("   Please run the training script first:")
            print("   docker-compose exec vision-service python train.py")
    except Exception as e:
        print(f"❌ Error loading model: {e}")


# Include routers
app.include_router(predict.router, prefix="/api", tags=["prediction"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Thyroid Segmentation Vision Service",
        "status": "running",
        "endpoints": {"predict": "/api/predict", "health": "/api/health"},
    }
