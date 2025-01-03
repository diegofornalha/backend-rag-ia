"""Rotas de health check."""

from fastapi import APIRouter, Response

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Response:
    """
    Endpoint leve para verificar a saúde da API.
    Retorna 200 OK se a API estiver funcionando.
    """
    return Response(status_code=200) 