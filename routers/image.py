import json
import base64
import datetime
import os
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from pydantic import BaseModel
from google import genai
from google.genai import types

from core.database import get_chat_collection
from core.security import get_current_user

router = APIRouter(prefix="/image", tags=["AI Image Generation Engine"])

class ImageGenerationRequest(BaseModel):
    prompt: str
    session_id: str  

async def log_image_to_mongodb(session_id_str: str, history_list: list, user_email: str):
    chat_collection = get_chat_collection()
    if chat_collection is None:
        print("🚨 Image DB Log Failure: Chat collection is not initialized.")
        return

    try:
        await chat_collection.update_one(
            {"_id": session_id_str},
            {
                "$set": {
                    "user_email": user_email,
                    "messages": history_list,
                    "chat_mode": "image_generation",
                    "title": "AI Image Workspace",
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }
            },
            upsert=True
        )
    except Exception as e:
        print(f"🚨 Image DB Log Thread Failure: {str(e)}")

@router.post("/generate")
async def generate_creative_image(
    req: ImageGenerationRequest, 
    background_tasks: BackgroundTasks, 
    current_user: dict = Depends(get_current_user)
):
    try:
        user_email = current_user.get("sub", "guest_user")
        
        api_key_str = os.environ.get("GEMINI_API_KEY")
        if not api_key_str:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="GEMINI_API_KEY pipeline variable is unconfigured."
            )
            
        # Amfani da sabon Client daga google-genai
        client = genai.Client(api_key=api_key_str)

        # Kirar hoton Imagen 3 ta amfani da sabon SDK
        result = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=req.prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        
        chat_collection = get_chat_collection()
        
        if result.generated_images:
            for generated_image in result.generated_images:
                # Ciro hoton daga bytes dinsa
                base64_image = base64.b64encode(generated_image.image.image_bytes).decode("utf-8")
                full_image_uri = f"data:image/jpeg;base64,{base64_image}"
                
                history = []
                if chat_collection is not None:
                    existing_chat = await chat_collection.find_one({"_id": req.session_id})
                    if existing_chat:
                        history = existing_chat.get("messages", [])
                
                history.append({"role": "user", "content": f"Kera mini hoton: {req.prompt}"})
                history.append({"role": "model", "content": "[Generated Image Asset UI Ready]", "image_url": full_image_uri})
                
                background_tasks.add_task(log_image_to_mongodb, req.session_id, history, user_email)
                
                return {
                    "status": "success",
                    "prompt": req.prompt,
                    "mime_type": "image/jpeg",
                    "image_data": full_image_uri
                }
            
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image generation engine returned empty grid.")
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))