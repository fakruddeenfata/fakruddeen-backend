import base64
import datetime
import os
import json
import tempfile
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import google.generativeai as genai

from core.database import get_chat_collection, get_redis_client
from core.security import get_current_user
from schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["AI Advanced Chat Engine"])

def limit_context_history(history: list, max_turns: int = 20) -> list:
    if len(history) <= max_turns * 2:
        return history
    return history[-(max_turns * 2):]

async def save_chat_to_mongodb(session_id_str: str, history_list: list, mode: str, user_email: str):
    chat_collection = get_chat_collection()
    if chat_collection is None:
        return

    try:
        title = f"Fata AI Ultra ({mode.capitalize()} Mode)"
        await chat_collection.update_one(
            {"_id": session_id_str},
            {
                "$set": {
                    "user_email": user_email,
                    "messages": history_list,
                    "chat_mode": mode,
                    "title": title,
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
            },
            upsert=True
        )
    except Exception as e:
        print(f"🚨 Critical DB Log Error: {str(e)}")

@router.post("/stream")
async def dynamic_chat_stream(
    req: ChatRequest, 
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    try:
        user_email = current_user.get("sub", "guest_user")
        api_key_str = os.environ.get("GEMINI_API_KEY")
        
        if not api_key_str:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing.")

        # Initalize google-generativeai API
        genai.configure(api_key=api_key_str)
        
        chat_collection = get_chat_collection()
        redis_client = get_redis_client()

        cache_key = f"chat_session:{req.session_id}"
        cached_history = await redis_client.get(cache_key) if redis_client else None
        
        if cached_history:
            history = json.loads(cached_history)
        else:
            history = []
            if chat_collection is not None:
                existing_chat = await chat_collection.find_one({"_id": req.session_id})
                if existing_chat:
                    history = existing_chat.get("messages", [])

        # Format history into google-generativeai format
        formatted_history = []
        for msg in limit_context_history(history):
            if "content" in msg:
                role_type = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role_type, "parts": [msg["content"]]})

        # Process uploaded files or images if present
        uploaded_part = None
        if req.file_base64 and req.mime_type:
            clean_base64 = req.file_base64.split(",")[1] if "," in req.file_base64 else req.file_base64
            file_bytes = base64.b64decode(clean_base64)
            
            if "video" in req.mime_type or len(file_bytes) > 4 * 1024 * 1024:
                suffix = f".{req.mime_type.split('/')[-1]}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                
                uploaded_part = genai.upload_file(path=tmp_path)
                os.unlink(tmp_path)
            else:
                uploaded_part = {
                    "mime_type": req.mime_type,
                    "data": file_bytes
                }

        user_prompt_parts = []
        if req.message:
            user_prompt_parts.append(req.message)
        if uploaded_part:
            user_prompt_parts.append(uploaded_part)

        if not user_prompt_parts:
            user_prompt_parts.append("Hello")

        # Record user message in history
        history.append({"role": "user", "content": req.message or f"[Media Payload: {req.mime_type}]"})

        # Setup model instance
        system_instruction = "You are Fata AI Ultra Core, built by the engineer Fakruddeen."
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_instruction
        )

        # Start or continue chat session
        chat_session = model.start_chat(history=formatted_history)

        async def generate_chunks():
            full_response = ""
            try:
                response = chat_session.send_message(user_prompt_parts, stream=True)
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        yield chunk.text

                history.append({"role": "model", "content": full_response})
                limited_history = limit_context_history(history)
                
                if redis_client:
                    try:
                        await redis_client.setex(f"chat_session:{req.session_id}", 3600, json.dumps(limited_history))
                    except Exception as e:
                        print(f"⚠️ Redis error: {str(e)}")

                background_tasks.add_task(save_chat_to_mongodb, req.session_id, limited_history, req.chat_mode, user_email)

            except Exception as e:
                yield f"⚠️ Kuskure daga Gemini API: {str(e)}"

        return StreamingResponse(
            generate_chunks(), 
            media_type="text/plain"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))