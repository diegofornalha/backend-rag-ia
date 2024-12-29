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

@router.get("/documents")
async def list_documents(skip: int = 0, limit: int = 10):
    """Lista todos os documentos com paginação."""
    try:
        vector_store = VectorStore()
        documents = await vector_store.list_documents(skip=skip, limit=limit)
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Erro ao listar documentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Busca um documento específico pelo ID."""
    try:
        vector_store = VectorStore()
        document = await vector_store.get_document(doc_id)
        if not document:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return document
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao buscar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{doc_id}")
async def update_document(doc_id: str, document: Document):
    """Atualiza um documento existente."""
    try:
        vector_store = VectorStore()
        updated = await vector_store.update_document(doc_id, document.content, document.metadata)
        if not updated:
            raise HTTPException(status_code=404, detail="Documento não encontrado")
        return {
            "message": "Documento atualizado com sucesso",
            "document_id": doc_id
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro ao atualizar documento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 