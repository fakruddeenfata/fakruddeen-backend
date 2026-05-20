import os

class Settings:
    PROJECT_NAME: str = "Fakruddeen Backend"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:86454500@localhost:5432/fakruddeen_db"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

settings = Settings()
