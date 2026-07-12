from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: Optional[str] = Field(None, description="Sakon rubutu da user ya turo")
    session_id: str = Field(..., description="Keɓantaccen ID na wannan hira (Session ID)")
    file_base64: Optional[str] = Field(None, description="Fayil ɗin da aka turo idan akwai (Hoton/Takarda da aka juye zuwa Base64)")
    mime_type: Optional[str] = Field(None, description="Irin nau'in fayil ɗin, misali: image/jpeg, application/pdf")
    chat_mode: Optional[str] = Field("standard", description="Yanayin hira: standard, notebook, ko voice")