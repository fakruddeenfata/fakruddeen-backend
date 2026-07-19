import datetime
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
import json

# Dauko API key din
api_key = os.getenv("GEMINI_API_KEY")

# TILASTA WA SDK: Mun cire api_key a ciki, mun saka shi a matsayin custom header ta http_options
# Wannan ita ce kadai dabarar da ke sa makullin 'AQ.' yin aiki da sabon SDK ba tare da 401 Error ba.
client = genai.Client(
    http_options={
        "headers": {
            "x-goog-api-key": api_key
        }
    }
)

app = FastAPI(
    title="Fata AI Ultra Core Engine",
    version="2.0.0",
    description="Fata AI World Class Ultra-Scale Core Engine - Streaming Enabled"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/v2/chat/stream", tags=["Fata AI Core"])
async def stream_chat(request: ChatRequest):
    
    async def generate_ai_response():
        try:
            response = await client.aio.models.generate_content_stream(
                model='gemini-1.5-flash',
                contents=request.prompt,
            )
            
            async for chunk in response:
                if chunk.text:
                    payload = json.dumps({"chunk": chunk.text})
                    yield f"{payload}\n"
                    
        except Exception as e:
            error_payload = json.dumps({"chunk": f"Backend Connection Error: {str(e)}"})
            yield f"{error_payload}\n"

    return StreamingResponse(generate_ai_response(), media_type="text/event-stream")

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "system": "Fata AI Ultra Core Engine",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }