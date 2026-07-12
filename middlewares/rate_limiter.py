from fastapi import Request, HTTPException, status, Depends
from app.core.config import settings
from app.core.database import redis_client
from app.core.security import get_current_user

async def rate_limiter(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Middleware da ke duba adadin kiran da kowane user ke yi a cikin minti guda.
    Idan ya wuce iyaka, zai jefa kuskure na HTTP 429 ta atomatik.
    """
    user_email = current_user["sub"]
    rate_limit_key = f"rate_limit:{user_email}"
    
    try:
        # Duba adadin kiran da ya yi a halin yanzu
        current_requests = await redis_client.get(rate_limit_key)
        
        if current_requests is not None and int(current_requests) >= settings.RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Kun wuce iyakar tambayoyin da za ku iya yi a halin yanzu. Da fatan ku saurara na ɗan lokaci."
            )
        
        # Idan bai kai iyaka ba, ƙara kirga kiran da +1 ta amfani da pipeline don gudun gaske
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.incr(rate_limit_key)
            if current_requests is None:
                await pipe.expire(rate_limit_key, settings.RATE_LIMIT_WINDOW)
            await pipe.execute()
            
    except HTTPException:
        raise
    except Exception as e:
        # Idan Redis yana da matsala, kada mu katse users (Fail-open strategy)
        # A canza shi zuwa production logger idan an tafi live
        pass