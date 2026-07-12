import datetime
import jwt
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer()

def hash_password(password: str) -> str:
    """Juya kalmar sirri zuwa facce ta yadda ba za a iya karantawa ba."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Duba idan kalmar sirri ta yi daidai da wadda ke rumbun bayanai."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: datetime.timedelta) -> str:
    """Ƙirƙirar JWT Token na musamman don User."""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_bearer)) -> dict:
    """
    Dependency da ke duba Token na kowane mai neman amfani da tsarin.
    Idan babu token ko token ɗin ya mutu, zai kore shi ta atomatik.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Tantancewa ta gaza: Ba a sami bayanan asusu a cikin token ba."
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Tantancewa ta gaza: Token ɗinku ba daidai ba ne ko ya mutu."
        )