"""Storage Service - Database and File Management"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import reports, files

app = FastAPI(
    title="Storage Service",
    description="Database and file storage for medical reports",
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


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database when service starts"""
    init_db()
    print("✅ Storage service started")


# Include routers
app.include_router(reports.router, prefix="/api", tags=["reports"])
app.include_router(files.router, prefix="/api", tags=["files"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Storage Service",
        "status": "running",
        "endpoints": {"reports": "/api/reports", "files": "/api/files"},
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
