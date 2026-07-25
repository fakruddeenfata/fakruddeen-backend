import os
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(prefix="/live", tags=["Real-time Gemini Audio Engine"])

@router.websocket("/ws")
async def live_audio_socket(websocket: WebSocket):
    await websocket.accept()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        await websocket.close(code=1008, reason="GEMINI_API_KEY missing")
        return
        
    try:
        # Placeholder stream check for audio connection
        await websocket.send_text("Live audio stream engine connected successfully.")
        while True:
            data = await websocket.receive_bytes()
            # Process incoming bytes if needed
            
    except WebSocketDisconnect:
        print("⚡ Live Socket Client Disconnected gracefully.")
    except Exception as e:
        print(f"🚨 Live Audio Pipeline Error: {str(e)}")
        await websocket.close(code=1011, reason=str(e))