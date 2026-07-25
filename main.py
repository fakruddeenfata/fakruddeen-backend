import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Haɗa dukkan Routers ta hanyar amfani da sabon tsarin import
from core.database import connect_to_mongo, close_mongo_connection
from routers import auth, chat, image, files, live

# 1. Database Connection Lifespan Handler (Modern Async Context)
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚡ Starting Fata AI Core Engine...")
    await connect_to_mongo()
    print("🚀 Connected to MongoDB cluster successfully.")
    yield
    print("🛑 Shutting down Fata AI Core Engine...")
    await close_mongo_connection()
    print("💤 Database connections closed safely.")

# 2. Initialize the Core FastAPI Engine
app = FastAPI(
    title="Fata AI Ultra Core Engine",
    description="Next-Generation Enterprise AI Architecture for massive scalability, real-time multimodal streaming, live audio WebSockets, and advanced image generation.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 3. Advanced CORS Security Layer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Yardar da dukkan neman haɗi daga kowane fayil/browser
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Core Root Endpoint
@app.get("/", tags=["System Health"])
async def root_health_check():
    return {
        "status": "online",
        "engine": "Fata AI Ultra Core",
        "version": "2.0.0",
        "author": "Fakruddeen",
        "message": "Welcome to the central node of Fata AI. Use /docs for API visualization."
    }

# 5. Route Integration
app.include_router(auth.router, prefix="/api/v2")
app.include_router(chat.router, prefix="/api/v2")
app.include_router(image.router, prefix="/api/v2")
app.include_router(files.router, prefix="/api/v2")
app.include_router(live.router, prefix="/api/v2")