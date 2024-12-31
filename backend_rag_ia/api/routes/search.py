from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import time

from ..services.semantic_search import SemanticSearch
from ..models.schemas import SearchQuery, SearchResponse, SearchResult
from ..config.settings import get_settings

router = APIRouter()
semantic_search = SemanticSearch()
settings = get_settings()

@router.post("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery) -> SearchResponse:
    """
    Endpoint para busca semântica de documentos.
    Recebe uma query e retorna os documentos mais relevantes.
    """
    try:
        start_time = time.time()
        
        # Realiza a busca
        raw_results = await semantic_search.search(
            query.query,
            threshold=query.threshold,
            limit=query.limit
        )
        
        # Converte resultados para o formato esperado
        results = [
            SearchResult(
                id=doc.id,
                titulo=doc.titulo,
                conteudo=doc.conteudo,
                similarity=doc.similarity,
                metadata=doc.metadata,
                created_at=doc.created_at
            )
            for doc in raw_results
        ]
        
        execution_time = time.time() - start_time
        
        return SearchResponse(
            results=results,
            total=len(results),
            query=query.query,
            execution_time=execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        ) 