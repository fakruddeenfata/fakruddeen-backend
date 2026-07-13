import os
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Shigar da Gemini API Key dinka
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6KxeAsauh85yb0vRkDWKTvp15bLeau9p5nPIM0xhMqnbQ"

# Muna amfani da sabon babban library na Google GenAI
from google import genai

client = genai.Client()

from core.config import settings
from routers import auth, chat  

app = FastAPI(
    title="Fata AI Ultra Core Engine",
    version="2.0.0",
    description="Fata AI World Class Ultra-Scale Core Engine - Streaming Enabled"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)

# Tsarin data da Frontend zai rika tura mana
class ChatRequest(BaseModel):
    prompt: str

# Kofa ta musamman ta tattaunawa irin ta ChatGPT (Streaming)
@app.post("/api/v2/chat/stream", tags=["Fata AI Core"])
async def stream_chat(request: ChatRequest):
    
    def generate_ai_response():
        # Kira babban injin Gemini don ya rika kawo amsar daki-daki
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash', # Mafi sauri da inganci a yanzu
            contents=request.prompt,
        )
        for chunk in response:
            # Tura kalmomin daya bayan daya zuwa ga wayar mai amfani
            if chunk.text:
                yield chunk.text

    return StreamingResponse(generate_ai_response(), media_type="text/event-stream")

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "system": "Fata AI Ultra Core Engine",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }