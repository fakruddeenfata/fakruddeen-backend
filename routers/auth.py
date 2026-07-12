import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_pg_db
from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.models.user_model import User
from app.schemas.auth_schema import UserAuth, AuthResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/guest", response_model=AuthResponse)
async def create_guest_session(db: AsyncSession = Depends(get_pg_db)):
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    guest_uuid = f"guest_{now_ts}"
    guest_email = f"{guest_uuid}@fata.ai"
    hashed_pwd = hash_password(guest_uuid)
    
    new_user = User(email=guest_email, hashed_password=hashed_pwd, is_guest=True)
    db.add(new_user)
    await db.commit()
    
    expiration = datetime.timedelta(days=settings.GUEST_TOKEN_EXPIRE_DAYS)
    token = create_access_token({"sub": guest_email, "is_guest": True}, expires_delta=expiration)
    return {"access_token": token, "email": guest_email, "is_guest": True}

@router.post("/register", response_model=AuthResponse)
async def register_user(user: UserAuth, db: AsyncSession = Depends(get_pg_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalars().first()
    
    if db_user and not db_user.is_guest:
        raise HTTPException(status_code=400, detail="Wannan Email din an riga an yi rajista da shi.")
    
    hashed_pwd = hash_password(user.password)
    if db_user and db_user.is_guest:
        db_user.hashed_password = hashed_pwd
        db_user.is_guest = False
    else:
        new_user = User(email=user.email, hashed_password=hashed_pwd, is_guest=False)
        db.add(new_user)
        
    await db.commit()
    expiration = datetime.timedelta(days=settings.USER_TOKEN_EXPIRE_DAYS)
    token = create_access_token({"sub": user.email, "is_guest": False}, expires_delta=expiration)
    return {"access_token": token, "email": user.email, "is_guest": False}