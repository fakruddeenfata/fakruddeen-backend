import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import connect_to_mongo, close_mongo_connection
from routers import auth, chat, image, files, live

# Database Lifespan Handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚡ Starting Fata AI Core Engine...")
    await connect_to_mongo()
    print("🚀 Connected to MongoDB cluster successfully.")
    yield
    print("🛑 Shutting down Fata AI Core Engine...")
    await close_mongo_connection()
    print("💤 Database connections closed safely.")

# Initialize FastAPI
app = FastAPI(
    title="Fata AI Ultra Core Engine",
    description="Next-Generation Enterprise AI Architecture.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Security Layer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/", tags=["System Health"])
async def root_health_check():
    return {
        "status": "online",
        "engine": "Fata AI Ultra Core",
        "version": "2.0.0",
        "author": "Fakruddeen",
        "message": "Welcome to the central node of Fata AI."
    }

# Route Integrations
app.include_router(auth.router, prefix="/api/v2")
app.include_router(chat.router, prefix="/api/v2")
app.include_router(image.router, prefix="/api/v2")
app.include_router(files.router, prefix="/api/v2")
app.include_router(live.router, prefix="/api/v2")