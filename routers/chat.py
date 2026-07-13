import json
import base64
import datetime
import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types
from app.core.config import settings
from app.core.database import chat_collection, redis_client
from app.core.security import get_current_user
from app.schemas.chat_schema import ChatRequest
from app.middlewares.rate_limiter import rate_limiter

router = APIRouter(prefix="/chat", tags=["Chat Engine"])

# Amfani da sabon tsarin Client na google-genai library
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def limit_context_history(history: list, max_turns: int = 15) -> list:
    if len(history) <= max_turns * 2:
        return history
    return history[-(max_turns * 2):]

async def save_chat_to_mongodb(session_id_str: str, history_list: list, mode: str, user_email: str):
    try:
        title = "Notebook Chat" if mode == "notebook" else "Voice Chat" if mode == "voice" else "Standard Chat"
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
    except Exception:
        pass

@router.post("", dependencies=[Depends(rate_limiter)])
async def chat_endpoint(req: ChatRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    try:
        user_email = current_user["sub"]
        cache_key = f"chat_session:{req.session_id}"
        
        cached_history = await redis_client.get(cache_key)
        if cached_history:
            history = json.loads(cached_history)
        else:
            existing_chat = await chat_collection.find_one({"_id": req.session_id})
            if existing_chat:
                history = existing_chat.get("messages", [])
            else:
                history = []

        clean_base64 = None
        if req.file_base64 and req.mime_type:
            clean_base64 = req.file_base64.split(",")[1] if "," in req.file_base64 else req.file_base64

        if req.message:
            history.append({"role": "user", "content": req.message})
        elif clean_base64 and not req.message:
            history.append({"role": "user", "content": f"[Uploaded File: {req.mime_type}]"})
        
        gemini_contents = []
        for msg in limit_context_history(history):
            if msg["role"] == "user":
                gemini_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=msg["content"])]))
            else:
                gemini_contents.append(types.Content(role="model", parts=[types.Part.from_text(text=msg["content"])]))

        if clean_base64 and gemini_contents and gemini_contents[-1].role == "user":
            file_part = types.Part.from_bytes(data=base64.b64decode(clean_base64), mime_type=req.mime_type)
            gemini_contents[-1].parts.append(file_part)

        system_instruction = "You are Fata AI, an advanced global AI assistant created by Fakruddeen. Respond in the user's input language."
        chosen_model = 'gemini-2.5-flash'
        
        active_tools = [
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(code_execution=types.CodeExecution())
        ]

        if req.chat_mode == "notebook":
            chosen_model = 'gemini-2.5-pro'
            system_instruction += " You are in Notebook Mode. Focus heavily on data synthesis."
        elif req.chat_mode == "voice":
            system_instruction += " You are in Voice Chat Mode. Short, conversational responses only."

        config = types.GenerateContentConfig(tools=active_tools, system_instruction=system_instruction)
        
        # Mun gyara kiran zuwa daidai tsarin synchronous generator amma yana gudu cikin threads lafiya
        response_stream = client.models.generate_content_stream(
            model=chosen_model, contents=gemini_contents, config=config
        )

        async def generate_chunks(session_id_str: str, current_history_list: list, mode: str, email: str):
            full_response = ""
            # Don yin amfani da standard iterator a cikin async function
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    yield json.dumps({"chunk": chunk.text, "type": "text", "mode": mode}) + "\n"
            
            current_history_list.append({"role": "model", "content": full_response})
            limited_history = limit_context_history(current_history_list)
            
            ttl = settings.CACHE_TTL if hasattr(settings, 'CACHE_TTL') else 3600
            await redis_client.setex(f"chat_session:{session_id_str}", ttl, json.dumps(limited_history))
            background_tasks.add_task(save_chat_to_mongodb, session_id_str, limited_history, mode, email)

        return StreamingResponse(generate_chunks(req.session_id, history, req.chat_mode, user_email), media_type="application/json")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))