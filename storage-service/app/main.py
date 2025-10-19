"""Storage Service - File Storage for Images"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import files, reports

app = FastAPI(
    title="Storage Service",
    description="File storage for report images and masks",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize service"""
    print("✅ Storage service started")


# Include routers
app.include_router(files.router, prefix="/api", tags=["files"])
app.include_router(reports.router, prefix="/api", tags=["reports"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Storage Service",
        "status": "running",
        "endpoints": {"files": "/api/files"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
