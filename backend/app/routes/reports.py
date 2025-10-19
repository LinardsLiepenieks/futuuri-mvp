from fastapi import APIRouter, HTTPException
from app.config import STORAGE_SERVICE_URL, REPORTS_API_PREFIX
import httpx

router = APIRouter()


@router.get("/reports")
async def list_reports():
    """Proxy endpoint to fetch all reports from storage-service."""
    url = f"{STORAGE_SERVICE_URL}{REPORTS_API_PREFIX}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=10.0)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502, detail="Failed to fetch reports from storage service"
            )
        return resp.json()
