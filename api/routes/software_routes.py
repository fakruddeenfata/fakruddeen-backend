from fastapi import APIRouter
from services.software_service import SoftwareService

router = APIRouter()
software_service = SoftwareService()

@router.post("/create")
async def create_software(filename: str, code: str):
    """Create new software file with code"""
    result = software_service.create_software(filename, code)
    return result

@router.get("/list")
async def list_generated():
    """List all generated software files"""
    result = software_service.list_generated()
    return result
