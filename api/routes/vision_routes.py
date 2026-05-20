from fastapi import APIRouter
from services.vision_service import VisionService

router = APIRouter()
vision_service = VisionService()

@router.get("/capture")
async def capture_image():
    """Capture image from camera"""
    file = vision_service.capture_image()
    if file:
        return {"message": "Image captured successfully", "file": file}
    return {"error": "Failed to capture image"}

@router.post("/detect-faces")
async def detect_faces(file: str):
    """Detect faces in an uploaded image file"""
    results = vision_service.detect_faces(file)
    return {"faces_detected": results}
