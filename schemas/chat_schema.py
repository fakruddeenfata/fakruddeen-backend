from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: Optional[str] = None
    session_id: str
    chat_mode: str = "standard"  # Zaba tsakanin: standard, notebook, voice, thinking
    file_base64: Optional[str] = None
    mime_type: Optional[str] = None
    thinking_budget: Optional[int] = 2048  # Adadin tokens da aka ware wa AI don yin tunani mai zurfi