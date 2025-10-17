from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def read_root():
    return {"message": "Welcome to Medical Report API"}


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
