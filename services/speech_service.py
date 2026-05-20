import speech_recognition as sr
import pyttsx3

class SpeechService:
    def __init__(self):
        # Initialize recognizer and TTS engine
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()

    def recognize_speech(self, audio_file: str) -> str:
        """Convert speech from audio file to text"""
        with sr.AudioFile(audio_file) as source:
            audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError:
                return "Speech recognition service unavailable"

    def speak_text(self, text: str):
        """Convert text to speech"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
