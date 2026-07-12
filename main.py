import os
import datetime

# Shigar da Gemini API Key dinka a tsarin kwamfutar
os.environ["GEMINI_API_KEY"] = "AQ.Ab8RN6KxeAsauh85yb0vRkDWKTvp15bLeau9p5nPIM0xhMqnbQ"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# An cire "app." tunda 'core' da 'routers' suna mataki daya da main.py
from core.config import settings
from routers import auth, chat  

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Fata AI World Class Ultra-Scale Core Engine"
)

# TSARIN CROWD PROTECTION (CORS MIDDLEWARE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # A canza shi zuwa takaitaccen domain dinku idan an tafi production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HAƊA KOWACE ƘOFA TA API (ROUTERS)
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }