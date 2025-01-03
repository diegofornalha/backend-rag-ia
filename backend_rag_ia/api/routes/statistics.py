"""Rotas de estatísticas."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from backend_rag_ia.utils.logging_config import logger

router = APIRouter(prefix="/api/v1", tags=["statistics"])

@router.get("/statistics")
async def get_statistics() -> dict[str, Any]:
    """Retorna estatísticas gerais do sistema.
    
    Returns:
        Dicionário com estatísticas:
        - total_documents: Total de documentos
        - total_embeddings: Total de embeddings
        - average_document_size: Tamanho médio dos documentos
        - last_update: Data da última atualização
    """
    try:
        # TODO: Implementar lógica de estatísticas usando VectorStore
        return {
            "total_documents": 0,
            "total_embeddings": 0,
            "average_document_size": 0,
            "last_update": datetime.now(UTC).isoformat()
        }
    except Exception as err:
        logger.exception("Erro ao obter estatísticas: %s", err)
        raise HTTPException(status_code=500, detail=str(err)) from err 