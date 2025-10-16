from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Medical Report API",
    description="Backend API for medical report system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Welcome to Medical Report API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an image file and return basic information about it.
    """
    # Get file information
    file_info = {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": 0,  # We'll calculate this
    }

    # Read and discard the file content to get size
    # (In a real app, you'd save this somewhere)
    content = await file.read()
    file_info["size_bytes"] = len(content)

    # Reset file position (not necessary for this simple example)
    await file.seek(0)

    return {
        "message": "Image received successfully",
        "file_info": file_info,
        "report_id": 123,  # Dummy ID for now
    }
