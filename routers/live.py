import os
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google import genai

router = APIRouter(prefix="/live", tags=["Real-time Gemini Audio Engine"])

@router.websocket("/ws")
async def live_audio_socket(websocket: WebSocket):
    await websocket.accept()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        await websocket.close(code=1008, reason="GEMINI_API_KEY missing")
        return
        
    client = genai.Client(api_key=api_key)
    model = "gemini-2.0-flash-exp" # Low latency multimodal engine
    
    try:
        # Establish persistent live connection pipeline
        async with client.aio.live.connect(model=model, config={"response_modalities": ["AUDIO"]}) as session:
            async def receive_from_client():
                while True:
                    data = await websocket.receive_bytes()
                    await session.send(input={"data": data, "mime_type": "audio/pcm"}, end_of_turn=False)

            async def send_to_client():
                async for response in session.receive():
                    if response.data:
                        await websocket.send_bytes(response.data)

            await asyncio.gather(receive_from_client(), send_to_client())
            
    except WebSocketDisconnect:
        print("⚡ Live Socket Client Disconnected gracefully.")
    except Exception as e:
        print(f"🚨 Live Audio Pipeline Error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))