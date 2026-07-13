import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
import json

# Initialize GenAI Client - yana ɗaukar GEMINI_API_KEY ta atomatik daga Render environment
client = genai.Client()

app = FastAPI(
    title="Fata AI Ultra Core Engine",
    version="2.0.0",
    description="Fata AI World Class Ultra-Scale Core Engine - Streaming Enabled"
)

# Robust Cross-Origin Pipeline (An gyara don streaming ya yi aiki ba tare da matsalar CORS ba)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False, # Dole ne ya zama False tunda an yi amfani da ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/v2/chat/stream", tags=["Fata AI Core"])
async def stream_chat(request: ChatRequest):
    
    # An canza zuwa async generator don FastAPI ya iya streaming ba tare da block ba
    async def generate_ai_response():
        try:
            # Kiran sabon Google GenAI SDK don fitar da bayanan jere-jere
            response = client.models.generate_content_stream(
                model='gemini-2.5-flash',
                contents=request.prompt,
            )
            
            for chunk in response:
                # Tabbatar cewa chunk ɗin yana da rubutu kafin a tura shi
                if chunk.text:
                    payload = json.dumps({"chunk": chunk.text})
                    yield f"{payload}\n"
        except Exception as e:
            # Idan an sami matsala wajen kiran Gemini API, a tura kuskuren zuwa frontend
            error_payload = json.dumps({"chunk": f"Error: {str(e)}"})
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