"""API principal do backend."""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend_rag_ia.constants import (
    HTTP_BAD_REQUEST,
    HTTP_SERVER_ERROR,
)
from backend_rag_ia.exceptions import (
    BaseError,
    DatabaseError,
    EmbeddingError,
)
from backend_rag_ia.services.semantic_search import SemanticSearch
from backend_rag_ia.utils.logging_config import logger

# Cria app
app = FastAPI(
    title="Backend RAG IA",
    description="API para busca semântica em documentos",
    version="1.0.0",
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serviço de busca
search_service = SemanticSearch()


def _handle_search_error(error: Exception) -> dict[str, Any]:
    """Trata erros da busca.

    Args:
        error: Erro ocorrido

    Returns:
        Resposta de erro formatada
    """
    logger.exception("Erro na busca: %s", error)

    if isinstance(error, EmbeddingError):
        return {
            "error": "Erro ao gerar embedding",
            "details": str(error),
        }

    if isinstance(error, DatabaseError):
        return {
            "error": "Erro no banco de dados",
            "details": str(error),
        }

    if isinstance(error, BaseError):
        return {
            "error": error.message,
            "details": str(error),
        }

    return {
        "error": "Erro interno",
        "details": str(error),
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Verifica saúde da API."""
    try:
        return {"status": "healthy", "message": "API está funcionando normalmente"}
    except Exception as e:
        logger.exception("Erro no health check: %s", e)
        return {"status": "unhealthy", "message": str(e)}


@app.get("/search")
async def search(query: str) -> dict[str, Any]:
    """Realiza busca semântica.

    Args:
        query: Texto para buscar

    Returns:
        Resultados da busca

    Raises:
        HTTPException: Se houver erro na busca
    """
    try:
        # Valida query
        if not query:
            raise HTTPException(
                status_code=HTTP_BAD_REQUEST,
                detail="Query não pode ser vazia",
            )

        # Realiza busca
        results = await search_service.search(query)

        # Retorna resultados
        return {
            "query": query,
            "results": results,
        }

    except Exception as e:
        # Trata erro
        error_response = _handle_search_error(e)
        raise HTTPException(
            status_code=HTTP_SERVER_ERROR,
            detail=error_response,
        ) from e


@app.exception_handler(Exception)
async def global_exception_handler(exc: Exception) -> dict[str, Any]:
    """Handler global de exceções.

    Args:
        exc: Exceção ocorrida

    Returns:
        Resposta de erro formatada
    """
    logger.exception("Erro não tratado: %s", exc)
    return {
        "error": "Erro interno",
        "details": str(exc),
    }
