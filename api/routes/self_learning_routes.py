from fastapi import APIRouter
from core.self_learning import SelfLearningEngine

router = APIRouter()
self_learning_engine = SelfLearningEngine()

@router.post("/log-error")
async def log_error(service: str, error_message: str):
    """Log an error for self-learning"""
    result = self_learning_engine.log_error(service, error_message)
    return result

@router.get("/suggest-improvement")
async def suggest_improvement():
    """Suggest improvements based on error logs"""
    result = self_learning_engine.suggest_improvement()
    return result
