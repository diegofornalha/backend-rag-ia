"""
Rotas da API do Oráculo.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from services.vector_store import VectorStore
from models.database import Document, DocumentCreate
from services.supabase_client import supabase

router = APIRouter()
logger = logging.getLogger(__name__)

class DocumentInput(BaseModel):
    """Modelo para input de documento."""
    content: str
    metadata: Dict[str, Any] = {}
    document_hash: Optional[str] = None

class QueryInput(BaseModel):
    """Modelo para input de busca."""
    query: str
    k: Optional[int] = 4

@router.post("/documents/", status_code=201)
async def add_document(document: DocumentInput) -> Dict[str, Any]:
    """
    Adiciona um documento ao store.
    
    Args:
        document: Documento a ser adicionado.
        
    Returns:
        Dict com mensagem de sucesso ou erro.
    """
    try:
        vector_store = VectorStore()
        
        # Extrai o document_hash do input
        document_hash = document.document_hash
        metadata = document.metadata
        
        # Adiciona o document_hash aos metadados se fornecido
        if document_hash:
            metadata["document_hash"] = document_hash
        
        result = await vector_store.add_document(
            content=document.content,
            metadata=metadata
        )
        
        if result:
            return {
                "message": "Documento adicionado com sucesso",
                "document": result.model_dump()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Erro ao adicionar documento"
            )
            
    except Exception as e:
        logger.error(f"Erro ao adicionar documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search(query_input: QueryInput) -> List[Dict[str, Any]]:
    """
    Realiza busca por similaridade.
    
    Args:
        query_input: Query e número de resultados.
        
    Returns:
        Lista de documentos similares.
    """
    try:
        vector_store = VectorStore()
        results = await vector_store.search(
            query=query_input.query,
            k=query_input.k
        )
        
        return [doc.model_dump() for doc in results]
        
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: int) -> Dict[str, str]:
    """
    Remove um documento do store.
    
    Args:
        doc_id: ID do documento.
        
    Returns:
        Dict com mensagem de sucesso ou erro.
    """
    try:
        vector_store = VectorStore()
        success = await vector_store.delete_document(doc_id)
        if success:
            return {"message": "Documento removido com sucesso"}
        else:
            raise HTTPException(
                status_code=404,
                detail="Documento não encontrado"
            )
            
    except Exception as e:
        logger.error(f"Erro ao remover documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/check/{document_hash}")
async def check_document_exists(document_hash: str) -> Dict[str, bool]:
    """
    Verifica se um documento já existe pelo hash.
    
    Args:
        document_hash: Hash do documento.
        
    Returns:
        Dict indicando se o documento existe.
    """
    try:
        result = supabase.table("documents").select("id").eq("document_hash", document_hash).execute()
        exists = bool(result.data)
        return {"exists": exists}
            
    except Exception as e:
        logger.error(f"Erro ao verificar documento: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 