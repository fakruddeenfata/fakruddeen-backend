import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Fata AI Ultra Core Engine")

# Bada damar shiga daga kowane fanni (CORS) domin HTML din ya samu damar kira
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dauko API Key din kai tsaye daga Render Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Wannan zai bayyana a Render Logs idan ba a saita Key din ba
    print("WARNING: GEMINI_API_KEY is not set in environment variables!")

# Tilasta wa SDK yin amfani da takamaiman API Key din da ka samar
# Wannan yana hana SDK din amfani da OAuth2/Google Cloud credentials da ke kawo kuskuren 401
client = genai.Client(api_key=GEMINI_API_KEY)

# Pydantic Schema da ke karbar bayanai daga HTML (An canza zuwa prompt)
class ChatRequest(BaseModel):
    prompt: str
    session_id: str
    chat_mode: str = "standard"
    file_base64: str = ""
    mime_type: str = ""

@app.post("/api/v2/chat/stream")
async def stream_chat(request: ChatRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500, 
            detail="Backend Configuration Error: GEMINI_API_KEY is missing on Render."
        )
        
    # Zabar model din da ya dace dangane da yanayin (Mode) da aka zaba
    model_name = "gemini-1.5-pro" if request.chat_mode == "notebook" else "gemini-1.5-flash"
    
    contents = []
    
    # Idan mai amfani ya tura fayil (Base64)
    if request.file_base64 and request.mime_type:
        try:
            file_part = types.Part.from_bytes(
                data=bytes(request.file_base64, "utf-8"),
                mime_type=request.mime_type
            )
            contents.append(file_part)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid file payload: {str(e)}")
            
    # Sanya rubutun prompt din a cikin contents
    if request.prompt:
        contents.append(request.prompt)
        
    if not contents:
        raise HTTPException(status_code=400, detail="Either prompt or file must be provided.")

    async def generate_chunks():
        try:
            # Kiran Gemini API ta hanyar Stream
            response = client.models.generate_content_stream(
                model=model_name,
                contents=contents
            )
            
            for chunk in response:
                if chunk.text:
                    # Tura sakamakon a matsayin JSON chunk zuwa HTML dashboard
                    yield json.dumps({"chunk": chunk.text}) + "\n"
                    
        except Exception as e:
            # Tura kuskure idan wani abu ya faru lokacin kiran Gemini
            yield json.dumps({"chunk": f"\n[Backend Error: {str(e)}]"}) + "\n"

    return StreamingResponse(generate_chunks(), media_type="application/x-ndjson")

if __name__ == "__main__":
    import uvicorn
    # Gudanar da app din a port din da Render ya samar ta atomatik
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)