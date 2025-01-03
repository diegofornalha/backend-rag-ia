"""Rotas de health check."""

from datetime import UTC, datetime
import os
from typing import Dict, Any

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from backend_rag_ia.config.settings import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()

@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> JSONResponse:
    """
    Endpoint para verificar a saúde da API.
    Retorna status e informações do sistema.
    
    Este endpoint é otimizado para ser rápido e leve,
    pois é usado pelo Render para health checks.
    """
    try:
        # Resposta rápida sem validações pesadas
        response = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT
        }
        
        # Retorna 200 com cache curto
        return JSONResponse(
            content=response,
            headers={
                "Cache-Control": "no-cache, max-age=0",
                "X-Health-Check": "true"
            }
        )
        
    except Exception as e:
        # Retorna 503 em caso de erro
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            },
            status_code=503
        ) 