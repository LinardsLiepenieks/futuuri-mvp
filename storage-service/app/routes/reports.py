"""Report endpoints and finalize logic"""

from fastapi import APIRouter, HTTPException
import os
import shutil
import sqlite3
from pathlib import Path
import uuid
from typing import Optional

router = APIRouter()

# Final storage directories (same as files.py)
REPORTS_DIR = "/app/data/uploads/reports"
MASKS_DIR = "/app/data/uploads/masks"
STAGING_DIR = "/app/data/uploads/staging"
DB_PATH = "/app/data/database.db"


def ensure_dirs():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(MASKS_DIR, exist_ok=True)
    os.makedirs(STAGING_DIR, exist_ok=True)


def db_connect():
    return sqlite3.connect(DB_PATH)


def finalize_report_if_ready(report_id: str) -> Optional[dict]:
    """If both report image and mask exist in staging for report_id,
    move them to final dirs and insert a row into reports table. Returns
    the inserted DB row dict on success, or None if not ready yet.
    """
    staging = Path(STAGING_DIR) / report_id
    if not staging.exists():
        return None

    # Find staged files
    report_file = None
    mask_file = None
    for p in staging.iterdir():
        if p.name.endswith("_mask.png"):
            mask_file = p
        else:
            report_file = p

    if not report_file or not mask_file:
        return None

    ensure_dirs()

    # Move files to final locations
    final_report_path = os.path.join(REPORTS_DIR, f"{report_id}_{report_file.name}")
    final_mask_path = os.path.join(MASKS_DIR, f"{report_id}_mask.png")

    shutil.move(str(report_file), final_report_path)
    shutil.move(str(mask_file), final_mask_path)

    # Remove staging dir
    try:
        shutil.rmtree(staging)
    except Exception:
        pass

    # Insert into DB
    conn = db_connect()
    cur = conn.cursor()
    # Ensure reports table exists (safety)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT NOT NULL UNIQUE,
            report_image_path TEXT,
            mask_image_path TEXT,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
            updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
        """
    )
    cur.execute(
        "INSERT INTO reports (report_id, report_image_path, mask_image_path) VALUES (?, ?, ?)",
        (report_id, final_report_path, final_mask_path),
    )
    conn.commit()
    conn.close()

    return {
        "report_id": report_id,
        "report_image_path": final_report_path,
        "mask_image_path": final_mask_path,
    }


@router.post("/reports")
async def create_report():
    """Create a new report in staging. No DB row or final files are created until both images are uploaded.

    Returns a `report_id` which must be used for subsequent upload calls.
    """
    report_id = str(uuid.uuid4())
    staging_path = os.path.join(STAGING_DIR, report_id)
    os.makedirs(staging_path, exist_ok=True)
    return {"success": True, "report_id": report_id}


@router.get("/reports")
async def list_reports():
    """Return all reports from the database (simple demo listing)."""
    # Ensure DB exists
    conn = db_connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id TEXT NOT NULL UNIQUE,
            report_image_path TEXT,
            mask_image_path TEXT,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
            updated_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
        """
    )
    conn.commit()
    cur.execute(
        "SELECT report_id, report_image_path, mask_image_path, created_at, updated_at FROM reports ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append(
            {
                "report_id": r[0],
                "report_image_path": r[1],
                "mask_image_path": r[2],
                "created_at": r[3],
                "updated_at": r[4],
            }
        )

    return {"success": True, "items": items}
