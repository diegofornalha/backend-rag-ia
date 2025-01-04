"""Rotas de health check."""

from fastapi import APIRouter, Response

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check(response: Response) -> dict:
    """Endpoint minimalista para health check."""
    response.status_code = 200
    return {"status": "ok"} 