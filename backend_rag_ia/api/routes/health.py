"""Rotas de health check."""

from datetime import UTC, datetime
from typing import Dict
from fastapi import APIRouter
from backend_rag_ia.models.schemas import HealthResponse
from backend_rag_ia.config.settings import get_settings

router = APIRouter(tags=["health"])

settings = get_settings()

@router.get("/health", response_model=HealthResponse)
async def health_check() -> Dict[str, str]:
    """
    Endpoint para verificar a saúde da API.
    Retorna status e informações do sistema.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime": 0.0  # TODO: Implementar cálculo de uptime
    } 