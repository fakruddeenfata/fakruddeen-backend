import datetime
import uuid
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from core.database import get_database
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
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    users_collection = db["users"]
    
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    hashed_pw = get_password_hash(user_data.password)
    await users_collection.insert_one({
        "email": user_data.email,
        "hashed_password": hashed_pw,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "role": "user"
    })
    return {"message": "User registered successfully", "email": user_data.email}

@router.post("/login")
async def login_user(user_data: UserLogin):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    users_collection = db["users"]
    
    user = await users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = datetime.timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user_data.email, "role": user.get("role", "user")},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}