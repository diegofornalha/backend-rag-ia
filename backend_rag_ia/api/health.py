"""Rotas de health check."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Verifica a saúde da API.

    Returns:
        Status da API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }
