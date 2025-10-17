"""File upload and retrieval endpoints"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report
from datetime import datetime
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "/app/data/uploads"
RESULTS_DIR = "/app/data/results"


@router.post("/files/upload/{report_id}/original")
async def upload_original_image(
    report_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload original image for a report"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{report_id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update report
    report.original_image_path = file_path
    report.updated_at = datetime.utcnow()
    db.commit()

    print(f"📁 Saved original image: {file_path}")
    return {"success": True, "path": file_path, "filename": file.filename}


@router.post("/files/upload/{report_id}/mask")
async def upload_segmentation_mask(
    report_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload segmentation mask for a report"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    # Save file
    file_path = os.path.join(RESULTS_DIR, f"{report_id}_mask.png")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update report
    report.segmentation_mask_path = file_path
    report.updated_at = datetime.utcnow()
    db.commit()

    print(f"📁 Saved segmentation mask: {file_path}")
    return {"success": True, "path": file_path}


@router.get("/files/{report_id}/original")
async def get_original_image(report_id: str, db: Session = Depends(get_db)):
    """Retrieve original image for a report"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.original_image_path or not os.path.exists(report.original_image_path):
        raise HTTPException(status_code=404, detail="Original image not found")

    return FileResponse(report.original_image_path)


@router.get("/files/{report_id}/mask")
async def get_segmentation_mask(report_id: str, db: Session = Depends(get_db)):
    """Retrieve segmentation mask for a report"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.segmentation_mask_path or not os.path.exists(
        report.segmentation_mask_path
    ):
        raise HTTPException(status_code=404, detail="Segmentation mask not found")

    return FileResponse(report.segmentation_mask_path)
