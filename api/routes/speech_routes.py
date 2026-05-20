from fastapi import APIRouter, UploadFile, File
from services.speech_service import SpeechService

router = APIRouter()
speech_service = SpeechService()

@router.post("/recognize")
async def recognize_speech(file: UploadFile = File(...)):
    """Recognize speech from uploaded audio file"""
    with open("temp_audio.wav", "wb") as f:
        f.write(await file.read())
    text = speech_service.recognize_speech("temp_audio.wav")
    return {"recognized_text": text}

@router.post("/speak")
async def speak_text(text: str):
    """Convert text to speech"""
    speech_service.speak_text(text)
    return {"message": "Speech played successfully"}
