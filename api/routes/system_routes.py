from fastapi import APIRouter
from services.system_service import SystemService

router = APIRouter()
system_service = SystemService()

@router.post("/open")
async def open_application(app_name: str):
    """Open an application by name"""
    result = system_service.open_application(app_name)
    return result

@router.post("/command")
async def run_command(command: str):
    """Run a system command"""
    result = system_service.run_command(command)
    return result
