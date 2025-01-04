"""Rotas de health check."""

from fastapi import APIRouter, Response

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check() -> dict:
    """
    Endpoint leve para verificar a saúde da API.
    Retorna 200 OK se a API estiver funcionando.
    """
    return {"status": "ok"}
