from fastapi import APIRouter, HTTPException
from app.config import STORAGE_SERVICE_URL, REPORTS_API_PREFIX
import httpx
from typing import List, Dict
from app.config import FILES_API_PREFIX
import os
from fastapi import Request

router = APIRouter()


@router.get("/reports")
async def list_reports(request: Request):
    """Proxy endpoint to fetch all reports from storage-service and enrich with backend file URLs."""
    url = f"{STORAGE_SERVICE_URL}{REPORTS_API_PREFIX}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502, detail="Failed to fetch reports from storage service"
            )
        data = resp.json()

    items: List[Dict] = data.get("items", [])

    # Build backend-hosted base for proxying files
    # Use request.base_url to construct absolute backend URL
    backend_base = str(request.base_url).rstrip("/")

    enriched = []
    for it in items:
        report_id = it.get("report_id")
        report_image_path = it.get("report_image_path")
        mask_image_path = it.get("mask_image_path")

        filename = None
        if report_image_path:
            filename = os.path.basename(report_image_path)

        report_url = (
            f"{backend_base}{FILES_API_PREFIX}/{report_id}/report/{filename}"
            if filename
            else None
        )
        mask_url = (
            f"{backend_base}{FILES_API_PREFIX}/{report_id}/mask" if report_id else None
        )

        new_item = dict(it)
        new_item["report_image_url"] = report_url
        new_item["mask_image_url"] = mask_url
        enriched.append(new_item)

    return {"success": True, "items": enriched}
