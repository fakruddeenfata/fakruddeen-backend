import json
import base64
import datetime
import os
import tempfile
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from fastapi.responses import StreamingResponse
from google import genai
from google.genai import types

# Gyara imports
from core.database import chat_collection, redis_client
from core.security import get_current_user
from schemas.chat_schema import ChatRequest

router = APIRouter(prefix="/chat", tags=["AI Advanced Chat Engine"])

def limit_context_history(history: list, max_turns: int = 20) -> list:
    if len(history) <= max_turns * 2:
        return history
    return history[-(max_turns * 2):]

async def save_chat_to_mongodb(session_id_str: str, history_list: list, mode: str, user_email: str):
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
        user_email = current_user["sub"]
        api_key_str = os.environ.get("GEMINI_API_KEY")
        if not api_key_str:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment line is missing.")
            
        client = genai.Client(api_key=api_key_str)
        
        cache_key = f"chat_session:{req.session_id}"
        cached_history = await redis_client.get(cache_key) if redis_client else None
        
        if cached_history:
            history = json.loads(cached_history)
        else:
            existing_chat = await chat_collection.find_one({"_id": req.session_id})
            history = existing_chat.get("messages", []) if existing_chat else []

        uploaded_file_ref = None
        clean_base64 = None
        
        if req.file_base64 and req.mime_type:
            clean_base64 = req.file_base64.split(",")[1] if "," in req.file_base64 else req.file_base64
            file_bytes = base64.b64decode(clean_base64)
            
            if "video" in req.mime_type or len(file_bytes) > 4 * 1024 * 1024:
                suffix = f".{req.mime_type.split('/')[-1]}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file_bytes)
                    tmp_path = tmp.name
                
                uploaded_file_ref = client.files.upload(file=tmp_path)
                os.unlink(tmp_path)
            
        if req.message:
            history.append({"role": "user", "content": req.message})
        elif req.file_base64:
            history.append({"role": "user", "content": f"[High-Capacity Payload Injected: {req.mime_type}]"})
        
        gemini_contents = []
        for msg in limit_context_history(history):
            if "content" in msg:
                role_type = "user" if msg["role"] == "user" else "model"
                gemini_contents.append(types.Content(role=role_type, parts=[types.Part.from_text(text=msg["content"])]))

        if gemini_contents and gemini_contents[-1].role == "user":
            if uploaded_file_ref:
                gemini_contents[-1].parts.append(uploaded_file_ref)
            elif clean_base64:
                gemini_contents[-1].parts.append(types.Part.from_bytes(data=base64.b64decode(clean_base64), mime_type=req.mime_type))

        system_instruction = "You are Fata AI Ultra Core, the sovereign apex AI network built by the engineer Fakruddeen. Deliver absolute master-level analytical solutions."
        chosen_model = 'gemini-2.0-flash'
        
        active_tools = [
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(code_execution=types.CodeExecution())
        ]

        if req.chat_mode == "thinking":
            chosen_model = 'gemini-2.0-flash-thinking-exp'
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(thinking_budget=req.thinking_budget)
            )
        else:
            if req.chat_mode == "notebook":
                chosen_model = 'gemini-2.5-pro'
                system_instruction += " Execute strict semantic analysis and extreme structural logic synthesis."
            elif req.chat_mode == "voice":
                system_instruction += " Conversational core responsive framework: output short, absolute lightning sentences."
            
            config = types.GenerateContentConfig(
                tools=active_tools,
                system_instruction=system_instruction
            )
        
        response_stream = client.models.generate_content_stream(
            model=chosen_model, contents=gemini_contents, config=config
        )

        async def generate_chunks(session_id_str: str, current_history: list, mode: str, email: str):
            full_response = ""
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    yield json.dumps({"chunk": chunk.text, "type": "text"}) + "\n"
            
            current_history.append({"role": "model", "content": full_response})
            limited_history = limit_context_history(current_history)
            
            if redis_client:
                await redis_client.setex(f"chat_session:{session_id_str}", 3600, json.dumps(limited_history))
            background_tasks.add_task(save_chat_to_mongodb, session_id_str, limited_history, mode, email)

        return StreamingResponse(
            generate_chunks(req.session_id, history, req.chat_mode, user_email), 
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))