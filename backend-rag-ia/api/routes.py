from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from services.vector_store import VectorStore

router = APIRouter()
logger = logging.getLogger(__name__)

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class SearchQuery(BaseModel):
    query: str
    k: Optional[int] = 4

@router.post("/documents")
async def add_document(document: Document):
    """Adiciona um novo documento ao índice."""
    try:
        vector_store = VectorStore()
        result = await vector_store.add_document(document)
        return {
            "message": "Documento adicionado com sucesso",
            "document_id": result
        }
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Remove um documento do índice pelo ID."""
    try:
        vector_store = VectorStore()
        success = await vector_store.delete_document(doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return {
            "message": "Documento removido com sucesso",
            "document_id": doc_id
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao remover documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(query: SearchQuery):
    """Realiza busca semântica nos documentos."""
    try:
        vector_store = VectorStore()
        results = await vector_store.search(query.query, k=query.k)
        return {
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Verifica o status da API."""
    try:
        vector_store = VectorStore()
        status = await vector_store.health_check()
        return {
            "status": "healthy" if status else "unhealthy",
            "message": "API está funcionando normalmente"
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        } 