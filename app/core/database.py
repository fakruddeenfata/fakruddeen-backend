from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as aioredis
from app.core.config import settings

# 1. POSTGRESQL ASYNC CONFIG (Don Auth)
pg_engine = create_async_engine(
    settings.POSTGRES_URL, 
    pool_size=100, 
    max_overflow=50, 
    pool_recycle=1800
)
AsyncSessionLocal = async_sessionmaker(bind=pg_engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()

# 2. MONGODB ASYNC CONFIG (Don Chat History)
mongo_client = AsyncIOMotorClient(settings.MONGO_URL, maxPoolSize=500, minPoolSize=50)
mongo_db = mongo_client["fata_ai_chats"]
chat_collection = mongo_db["chat_history"]

# 3. REDIS ASYNC CONFIG (Don Caching da Rate Limiting)
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

# Generator don amfani da DB a kofofin API (PostgreSQL Dependency)
async def get_pg_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()