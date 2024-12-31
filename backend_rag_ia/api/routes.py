"""Rotas da API."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from backend_rag_ia.constants import (
    ERROR_SEARCH_FAILED,
    HTTP_BAD_REQUEST,
    HTTP_SERVER_ERROR,
)
from backend_rag_ia.exceptions import (
    ValidationError,
)
from backend_rag_ia.services.semantic_search import SemanticSearchManager
from backend_rag_ia.utils.logging_config import logger

router = APIRouter(prefix="/api/v1", tags=["search"])

def _validate_query(query: str) -> None:
    """Valida a query de busca.

    Args:
        query: Query a ser validada

    Raises:
        ValidationError: Se a query for inválida
    """
    if not query or not query.strip():
        raise ValidationError("Query não pode ser vazia")

def _handle_search_error(error: Exception) -> None:
    """Trata erros de busca.

    Args:
        error: Erro ocorrido

    Raises:
        HTTPException: Com detalhes do erro
    """
    logger.exception("Erro na busca: %s", error)
    if isinstance(error, ValidationError):
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST,
            detail=str(error),
        ) from error
    raise HTTPException(
        status_code=HTTP_SERVER_ERROR,
        detail=ERROR_SEARCH_FAILED.format(error=str(error)),
    ) from error

@router.post("/search")
async def search(query: str) -> dict[str, Any]:
    """Realiza busca semântica.

    Args:
        query: Query de busca

    Returns:
        Resultados da busca

    Raises:
        HTTPException: Se ocorrer algum erro
    """
    try:
        # Valida query
        _validate_query(query)

        # Realiza busca
        search_manager = SemanticSearchManager()
        results = await search_manager.search(query)

        # Retorna resultados
        return {
            "query": query,
            "results": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    except Exception as e:
        _handle_search_error(e)

@router.get("/history")
async def get_history() -> dict[str, Any]:
    """Retorna histórico de buscas.

    Returns:
        Histórico de buscas

    Raises:
        HTTPException: Se ocorrer algum erro
    """
    try:
        search_manager = SemanticSearchManager()
        history = search_manager.get_history()
        return {
            "history": history,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.exception("Erro ao obter histórico: %s", e)
        raise HTTPException(
            status_code=HTTP_SERVER_ERROR,
            detail=f"Erro ao obter histórico: {e}",
        ) from e

@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    """Retorna estatísticas de busca.

    Returns:
        Estatísticas de busca

    Raises:
        HTTPException: Se ocorrer algum erro
    """
    try:
        search_manager = SemanticSearchManager()
        stats = search_manager.get_stats()
        return {
            "stats": stats,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.exception("Erro ao obter estatísticas: %s", e)
        raise HTTPException(
            status_code=HTTP_SERVER_ERROR,
            detail=f"Erro ao obter estatísticas: {e}",
        ) from e
