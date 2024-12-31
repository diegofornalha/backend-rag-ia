import os
from enum import Enum

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/config", tags=["config"])

class SemanticMode(str, Enum):
    LOCAL = "local"
    RENDER = "render"
    AUTO = "auto"

class SemanticModeUpdate(BaseModel):
    mode: SemanticMode

@router.get("/semantic-mode")
async def get_semantic_mode():
    """Retorna o modo atual da busca semântica."""
    current_mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
    return {
        "mode": current_mode,
        "description": {
            "local": "Usando busca semântica local via Docker",
            "render": "Usando busca semântica remota via Render",
            "auto": "Modo automático com fallback"
        }.get(current_mode, "Modo desconhecido")
    }

@router.post("/semantic-mode")
async def update_semantic_mode(update: SemanticModeUpdate):
    """Atualiza o modo da busca semântica."""
    try:
        os.environ["SEMANTIC_SEARCH_MODE"] = update.mode.value
        return {
            "message": f"Modo alterado para {update.mode}",
            "mode": update.mode
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar modo: {e!s}"
        ) from e
