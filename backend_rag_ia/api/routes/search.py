"""Módulo para rotas de busca da API.

Este módulo fornece endpoints para busca semântica em documentos,
incluindo busca por similaridade e recomendações.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ...services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


class SearchResult(BaseModel):
    """Modelo de resultado de busca.

    Attributes
    ----------
    document_id : str
        ID do documento encontrado.
    title : str
        Título do documento.
    content : str
        Trecho relevante do conteúdo.
    score : float
        Pontuação de relevância.
    metadata : dict
        Metadados do documento.

    """

    document_id: str
    title: str
    content: str
    score: float
    metadata: dict


@router.get("/", response_model=list[SearchResult])
async def search_documents(
    query: str = Query(..., min_length=3),
    limit: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0)
) -> list[SearchResult]:
    """Realiza busca semântica nos documentos.

    Parameters
    ----------
    query : str
        Texto para busca.
    limit : int
        Número máximo de resultados.
    min_score : float
        Pontuação mínima para incluir resultado.

    Returns
    -------
    list[SearchResult]
        Lista de resultados ordenados por relevância.

    """
    service = SearchService()
    results = await service.search(query, limit, min_score)
    return results


@router.get("/similar/{document_id}", response_model=list[SearchResult])
async def get_similar_documents(
    document_id: str,
    limit: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0)
) -> list[SearchResult]:
    """Busca documentos similares a um documento específico.

    Parameters
    ----------
    document_id : str
        ID do documento de referência.
    limit : int
        Número máximo de resultados.
    min_score : float
        Pontuação mínima para incluir resultado.

    Returns
    -------
    list[SearchResult]
        Lista de documentos similares.

    """
    service = SearchService()
    results = await service.find_similar(document_id, limit, min_score)
    return results
