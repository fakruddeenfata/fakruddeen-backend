import os

class Settings:
    # PROJECT DETAILS
    PROJECT_NAME: str = "Fata AI Ultra"
    VERSION: str = "2.0.0"
    
    # SECURITY & JWT CONFIG (Idan babu a env, yana amfani da fallback amma an cire keys din a bayyane)
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "fata_ai_super_secret_core_key_2026")
    JWT_ALGORITHM: str = "HS256"
    GUEST_TOKEN_EXPIRE_DAYS: int = 7
    USER_TOKEN_EXPIRE_DAYS: int = 30
    
    # DATABASE URLS
    POSTGRES_URL: str = os.environ.get(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost/fata_auth"
    )
    MONGO_URL: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    
    # THIRD PARTY APIS (An cire key din gaba daya daga cikin kodi don tsaro!)
    GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
    
    # RATE LIMIT CONFIG
    RATE_LIMIT_WINDOW: int = 60  # Daƙiƙa guda (1 minute)
    RATE_LIMIT_MAX_REQUESTS: int = 20  # Iyakar tambayoyi 20 a minti guda
    CACHE_TTL: int = 3600  # Tsawon lokacin adana cache na hira (1 hour)

settings = Settings()

if not settings.GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set! System will fail to call Gemini models.")