import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Haɗa dukkan Routers ta hanyar amfani da sabon tsarin import
from core.database import connect_to_mongo, close_mongo_connection
from routers import auth, chat, image, files, live

# 1. Initialize the Core FastAPI Engine
app = FastAPI(
    title="Fata AI Ultra Core Engine",
    description="Next-Generation Enterprise AI Architecture for massive scalability, real-time multimodal streaming, live audio WebSockets, and advanced image generation.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 2. Advanced CORS Security Layer
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "https://fata-ai.pages.dev",
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Database Connection Lifespan Handlers
@app.on_event("startup")
async def startup_event():
    print("⚡ Starting Fata AI Core Engine...")
    await connect_to_mongo()
    print("🚀 Connected to MongoDB cluster successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Shutting down Fata AI Core Engine...")
    await close_mongo_connection()
    print("💤 Database connections closed safely.")

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