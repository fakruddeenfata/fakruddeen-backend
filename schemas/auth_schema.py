from pydantic import BaseModel, EmailStr, Field

class UserAuth(BaseModel):
    email: EmailStr = Field(..., description="Adireshin email na mai amfani da tsarin")
    password: str = Field(..., min_length=6, description="Kalmar sirri wadda ta kai aƙalla haruffa 6")

class AuthResponse(BaseModel):
    access_token: str
    email: EmailStr
    is_guest: bool