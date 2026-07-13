import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
import json

# Initialize GenAI Client - automatically picks up GEMINI_API_KEY from environment
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
    allow_credentials=False, # Crucial: Must be False when allow_origins is ["*"] to prevent browser block
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/v2/chat/stream", tags=["Fata AI Core"])
async def stream_chat(request: ChatRequest):
    def generate_ai_response():
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=request.prompt,
        )
        for chunk in response:
            if chunk.text:
                # Pack text securely inside a JSON line format matching the frontend layout
                payload = json.dumps({"chunk": chunk.text})
                yield f"{payload}\n"

    return StreamingResponse(generate_ai_response(), media_type="text/event-stream")

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "system": "Fata AI Ultra Core Engine",
        "version": "2.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }