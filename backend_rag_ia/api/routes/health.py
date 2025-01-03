"""Rotas de health check."""

from fastapi import APIRouter, Response
from datetime import UTC, datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(response: Response) -> dict:
    """
    Endpoint leve para verificar a saúde da API.
    Retorna status e timestamp.
    """
    response.status_code = 200
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat()
    } 