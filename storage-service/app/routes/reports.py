"""Report CRUD endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Report
from datetime import datetime
import json

router = APIRouter()


@router.post("/reports")
async def create_report(db: Session = Depends(get_db)):
    """Create a new report"""
    report = Report()
    db.add(report)
    db.commit()
    db.refresh(report)

    print(f"📝 Created new report: {report.id}")
    return {"success": True, "report": report.to_dict()}


@router.get("/reports/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get report by ID"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"success": True, "report": report.to_dict()}


@router.get("/reports")
async def list_reports(db: Session = Depends(get_db)):
    """List all reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()

    return {
        "success": True,
        "reports": [report.to_dict() for report in reports],
        "count": len(reports),
    }


@router.put("/reports/{report_id}/analysis")
async def update_analysis(
    report_id: str, analysis_data: dict, db: Session = Depends(get_db)
):
    """Update report with analysis results"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.analysis_results = json.dumps(analysis_data)
    report.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(report)

    print(f"📊 Updated analysis for report: {report_id}")
    return {"success": True, "report": report.to_dict()}


@router.put("/reports/{report_id}/status")
async def update_status(report_id: str, status: str, db: Session = Depends(get_db)):
    """Update report status"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.status = status
    report.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(report)

    print(f"✅ Updated status for report {report_id}: {status}")
    return {"success": True, "report": report.to_dict()}


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str, db: Session = Depends(get_db)):
    """Delete a report"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()

    print(f"🗑️  Deleted report: {report_id}")
    return {"success": True, "message": f"Report {report_id} deleted"}
