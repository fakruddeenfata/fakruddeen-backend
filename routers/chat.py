import os
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai

from core.database import get_chat_collection
from core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Chat Engine"])

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GEMINI_API_KEY pipeline variable is unconfigured."
            )

        # Configure API Key
        genai.configure(api_key=api_key)

        # Amfani da amintaccen sunan model tare da "models/" prefix
        model = genai.GenerativeModel("models/gemini-2.5-flash")

        def generate_chunks():
            try:
                # Stream response daga Gemini
                response = model.generate_content(req.message, stream=True)
                for chunk in response:
                    if hasattr(chunk, "text") and chunk.text:
                        yield chunk.text
            except Exception as e:
                # Idan aka samu matsala da gemini-2.5-flash, a gwada gemini-1.5-flash daki-daki
                try:
                    fallback_model = genai.GenerativeModel("models/gemini-1.5-flash")
                    response = fallback_model.generate_content(req.message, stream=True)
                    for chunk in response:
                        if hasattr(chunk, "text") and chunk.text:
                            yield chunk.text
                except Exception as fallback_err:
                    yield f"⚠️ Kuskure daga Gemini API: {str(fallback_err)}"

        return StreamingResponse(generate_chunks(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))