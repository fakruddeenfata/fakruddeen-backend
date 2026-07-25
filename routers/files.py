import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from google import genai

from core.security import get_current_user

router = APIRouter(prefix="/files", tags=["File Processing Engine"])

@router.post("/upload")
async def upload_file_to_gemini(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GEMINI_API_KEY pipeline variable is unconfigured."
            )

        # Adana fayil a gida (temporary local storage)
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # Amfani da sabon Client daga google-genai
        client = genai.Client(api_key=api_key)

        # Upload zuwa Gemini Files API
        uploaded_file = client.files.upload(file=temp_file_path)

        # Goge temporary file din bayan an gama upload
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return {
            "status": "success",
            "file_name": uploaded_file.name,
            "uri": uploaded_file.uri,
            "mime_type": uploaded_file.mime_type
        }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))