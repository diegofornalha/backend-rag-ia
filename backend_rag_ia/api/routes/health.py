from fastapi import APIRouter
from typing import Dict
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Endpoint para verificar a saúde da API.
    Retorna status e timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    } 