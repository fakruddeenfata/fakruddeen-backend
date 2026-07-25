import datetime
import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from jose import jwt

from core.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication System"])

class GuestResponse(BaseModel):
    access_token: str
    token_type: str
    email: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/guest", response_model=GuestResponse, status_code=status.HTTP_201_CREATED)
async def create_guest_session():
    try:
        guest_id = str(uuid.uuid4())[:8]
        guest_email = f"guest_{guest_id}@fata.ai"
        
        access_token_expires = datetime.timedelta(minutes=1440)
        access_token = create_access_token(
            data={"sub": guest_email, "role": "guest"},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": guest_email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to allocate guest context token: {str(e)}"
        )

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    return {"message": "Registration engine blueprint ready.", "email": user_data.email}