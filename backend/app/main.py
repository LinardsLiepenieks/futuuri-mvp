from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.routes import health
from app.routes import upload
from app.routes import reports
from app.routes import files

app = FastAPI(
    title="Medical Report API",
    description="Backend API for medical report system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(upload.router, tags=["upload"])
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(files.router, prefix="/api", tags=["files"])
