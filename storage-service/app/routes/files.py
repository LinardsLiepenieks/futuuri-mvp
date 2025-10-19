"""File upload and retrieval endpoints with staging and atomic commit"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil
from pathlib import Path

from .reports import finalize_report_if_ready

router = APIRouter()

# Final storage directories
REPORTS_DIR = "/app/data/uploads/reports"
MASKS_DIR = "/app/data/uploads/masks"

# Staging area for uploads until both files and report are present
STAGING_DIR = "/app/data/uploads/staging"


@router.post("/files/upload/{report_id}/report")
async def upload_report_file(report_id: str, file: UploadFile = File(...)):
    """Upload report image into staging for the given report_id."""
    # Ensure staging exists for this report
    staging_path = Path(STAGING_DIR) / report_id
    if not staging_path.exists():
        raise HTTPException(
            status_code=404, detail="Staging report not found. Create report first."
        )

    # Save to staging
    staged_name = f"{report_id}_{file.filename}"
    staged_path = staging_path / staged_name
    with open(staged_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Attempt to finalize (will only commit if mask also exists)
    result = finalize_report_if_ready(report_id)
    if result:
        return {"success": True, "committed": True, "path": result["report_image_path"]}

    return {"success": True, "committed": False, "path": str(staged_path)}


@router.post("/files/upload/{report_id}/mask")
async def upload_mask_file(report_id: str, file: UploadFile = File(...)):
    """Upload mask image into staging for the given report_id."""
    staging_path = Path(STAGING_DIR) / report_id
    if not staging_path.exists():
        raise HTTPException(
            status_code=404, detail="Staging report not found. Create report first."
        )

    # Save mask to staging with a consistent name
    staged_mask = staging_path / f"{report_id}_mask.png"
    with open(staged_mask, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Attempt to finalize
    result = finalize_report_if_ready(report_id)
    if result:
        return {"success": True, "committed": True, "path": result["mask_image_path"]}

    return {"success": True, "committed": False, "path": str(staged_mask)}


@router.get("/files/{report_id}/report/{filename}")
async def get_report_file(report_id: str, filename: str):
    """Retrieve report file for a report (final storage)"""
    file_path = os.path.join(REPORTS_DIR, f"{report_id}_{filename}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(file_path)


@router.get("/files/{report_id}/mask")
async def get_mask_file(report_id: str):
    """Retrieve mask file for a report (final storage)"""
    file_path = os.path.join(MASKS_DIR, f"{report_id}_mask.png")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Mask file not found")

    return FileResponse(file_path)
