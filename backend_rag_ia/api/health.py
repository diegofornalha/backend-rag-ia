from fastapi import APIRouter
import os
from datetime import datetime

router = APIRouter(prefix="/api/v1", tags=["health"])

@router.get("/health")
async def health_check():
    """Verifica o status da API e retorna informações do sistema."""
    semantic_mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
    mode_description = {
        "local": "Busca semântica local (Docker)",
        "render": "Busca semântica remota (Render)",
        "auto": "Busca semântica automática com fallback"
    }.get(semantic_mode, "Modo desconhecido")

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "semantic_search": {
            "mode": semantic_mode,
            "description": mode_description,
            "status": "active"
        }
    } 