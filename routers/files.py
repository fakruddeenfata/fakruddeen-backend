import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
import google.generativeai as genai

from core.security import get_current_user

router = APIRouter(prefix="/files", tags=["Multimodal Media Upload Pipeline"])

@router.post("/upload")
async def upload_media_to_gemini(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is missing.")
            
        genai.configure(api_key=api_key)
        
        suffix = f".{file.filename.split('.')[-1]}" if "." in file.filename else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        file_ref = genai.upload_file(path=tmp_path)
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "file_uri": file_ref.uri,
            "mime_type": file_ref.mime_type,
            "display_name": file_ref.display_name,
            "name": file_ref.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File Processing Engine Failed: {str(e)}")