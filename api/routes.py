from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from models.document import Document
from services.vector_store import VectorStore
import logging
import os

router = APIRouter()
logger = logging.getLogger(__name__)

# Inicialização do VectorStore com configurações otimizadas
vector_store = VectorStore(
    embedding_model="all-MiniLM-L6-v2",
    index_path="faiss_index",
    batch_size=32
)

class DocumentInput(BaseModel):
    content: str
    metadata: Dict[str, Any]

class QueryInput(BaseModel):
    query: str
    k: Optional[int] = 4

@router.post("/documents/", status_code=201)
async def add_documents(documents: List[DocumentInput], background_tasks: BackgroundTasks):
    """Adiciona documentos em background para não bloquear a API"""
    try:
        docs = [Document(content=doc.content, metadata=doc.metadata) for doc in documents]
        background_tasks.add_task(vector_store.add_documents, docs)
        return {"message": f"Processando {len(docs)} documentos em background"}
    except Exception as e:
        logger.error(f"Erro ao adicionar documentos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/")
async def search(query_input: QueryInput):
    """Realiza busca por similaridade"""
    try:
        results = await vector_store.similarity_search(
            query_input.query,
            query_input.k
        )
        return [
            {
                "content": doc.content,
                "metadata": doc.metadata,
                "embedding_id": doc.embedding_id
            }
            for doc in results
        ]
    except Exception as e:
        logger.error(f"Erro na busca: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Verifica a saúde da API"""
    try:
        # Verifica se o vector_store está inicializado
        if vector_store.index is None:
            return {"status": "error", "message": "Vector store não inicializado"}
        
        # Verifica o número de documentos no índice e na lista de documentos
        num_docs_index = vector_store.index.ntotal if vector_store.index else 0
        num_docs_list = len(vector_store.documents)
        
        # Verifica se há inconsistência entre o índice e a lista de documentos
        if num_docs_index != num_docs_list:
            logger.warning(f"Inconsistência: {num_docs_index} documentos no índice, mas {num_docs_list} na lista")
        
        return {
            "status": "healthy",
            "documents_loaded": num_docs_list,
            "documents_in_index": num_docs_index,
            "index_initialized": vector_store.index is not None
        }
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 