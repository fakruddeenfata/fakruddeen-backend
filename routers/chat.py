import os
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai

from core.database import get_chat_collection
from core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Chat Engine"])

class ChatRequest(BaseModel):
    message: str
    session_id: str

async def save_conversation(session_id: str, user_email: str, message: str, full_response: str):
    """
    Adana tattaunawa a MongoDB tare da cikakken saƙo (history).
    """
    chat_collection = get_chat_collection()
    if chat_collection is None:
        print("🚨 DB not initialized for conversation saving.")
        return
    
    try:
        history = []
        existing_chat = await chat_collection.find_one({"_id": session_id})
        if existing_chat:
            history = existing_chat.get("messages", [])
        
        history.append({"role": "user", "content": message})
        history.append({"role": "model", "content": full_response})
        
        await chat_collection.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "user_email": user_email,
                    "messages": history,
                    "chat_mode": "standard",
                    "title": "AI Chat Session",
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
            },
            upsert=True
        )
    except Exception as e:
        print(f"🚨 Conversation save error: {str(e)}")

@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="GEMINI_API_KEY pipeline variable is unconfigured."
            )

        client = genai.Client(api_key=api_key)
        user_email = current_user.get("sub", "guest_user")

        def generate_chunks():
            full_response = ""
            try:
                response = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=req.message
                )
                for chunk in response:
                    if hasattr(chunk, "text") and chunk.text:
                        full_response += chunk.text
                        yield chunk.text
            except Exception as e:
                print(f"⚠️ Primary Gemini error: {str(e)}")
                try:
                    response = client.models.generate_content_stream(
                        model='gemini-2.0-flash',
                        contents=req.message
                    )
                    for chunk in response:
                        if hasattr(chunk, "text") and chunk.text:
                            full_response += chunk.text
                            yield chunk.text
                except Exception as fallback_err:
                    err_msg = f"⚠️ Gemini fallback error: {str(fallback_err)}"
                    full_response += err_msg
                    yield err_msg
            
            # Adana cikakkiyar amsar sau guda ɗaya bayan an gama streaming
            if full_response:
                background_tasks.add_task(
                    save_conversation,
                    req.session_id,
                    user_email,
                    req.message,
                    full_response
                )

        return StreamingResponse(generate_chunks(), media_type="text/plain")

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"🚨 Unexpected chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat engine internal failure.")