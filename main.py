from fastapi import FastAPI
from api.routes import speech_routes, vision_routes, system_routes, software_routes

app = FastAPI(title="Fakruddeen Backend", version="1.0.0")

# Register routes
app.include_router(speech_routes.router, prefix="/speech", tags=["Speech"])
app.include_router(vision_routes.router, prefix="/vision", tags=["Vision"])
app.include_router(system_routes.router, prefix="/system", tags=["System"])
app.include_router(software_routes.router, prefix="/software", tags=["Software"])

@app.get("/")
def root():
    return {"message": "Fakruddeen Backend is running!"}
