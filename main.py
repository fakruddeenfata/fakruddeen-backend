import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
import json

# Initialize GenAI Client
client = genai.Client()

app = FastAPI(
    title="Fata AI Ultra Core Engine",
    version="2.0.0",
    description="Fata AI World Class Ultra-Scale Core Engine - Streaming Enabled"
)

# Robust Cross-Origin Pipeline (Fixed for seamless streaming)
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
    
    # Mun canza zuwa async generator mai amfani da client.aio
    async def generate_ai_response():
        try:
            # Amfani da client.aio.models yana tabbatar da async pipeline ya ga API key daidai
            response = await client.aio.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=request.prompt,
            )
            
            async for chunk in response:
                if chunk.text:
                    payload = json.dumps({"chunk": chunk.text})
                    yield f"{payload}\n"
                    
        except Exception as e:
            # Idan an sami kuskure (kamar 401), zai tura muku bayani ta JSON
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