from datetime import datetime
from typing import Dict, Any, Optional, List
from .base import BaseCluster
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from .utils.messages import MessageTemplate
from .utils.logger import get_logger

logger = get_logger(__name__, rag_debug=True)

class ProductionCluster(BaseCluster):
    """Implementação do cluster para ambiente de produção"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.model = SentenceTransformer(settings.MODEL_NAME)
        
    async def get_documents_count(self) -> int:
        """Retorna a contagem real de documentos do Supabase"""
        try:
            from main import supabase
            docs = supabase.table("documents").select("id").execute()
            return len(docs.data)
        except Exception as e:
            logger.error(MessageTemplate.DB_QUERY_ERROR.format(
                query="select documents count",
                error=str(e)
            ))
            return 0
        
    async def get_embeddings_count(self) -> int:
        """Retorna a contagem real de embeddings do Supabase"""
        try:
            from main import supabase
            embeddings = supabase.table("embeddings").select("id").execute()
            return len(embeddings.data)
        except Exception as e:
            logger.error(MessageTemplate.DB_QUERY_ERROR.format(
                query="select embeddings count",
                error=str(e)
            ))
            return 0
        
    async def get_health_check(self) -> Dict[str, Any]:
        """Retorna informações detalhadas de saúde do cluster de produção"""
        try:
            from main import supabase
            
            # Consulta documentos
            docs_count = await self.get_documents_count()
            
            # Consulta embeddings
            embeddings_count = await self.get_embeddings_count()
            
            # Busca a contagem da tabela de estatísticas
            stats = supabase.table("statistics").select("*").eq("key", "documents_count").execute()
            stored_count = stats.data[0]["value"] if stats.data else docs_count
            
            return {
                "status": "healthy",
                "message": "API está funcionando normalmente",
                "documents_count": stored_count,
                "embeddings_count": embeddings_count,
                "last_update": datetime.now().isoformat(),
                "model_info": {
                    "name": self.settings.MODEL_NAME,
                    "embedding_size": self.model.get_sentence_embedding_dimension()
                }
            }
        except Exception as e:
            logger.error(MessageTemplate.OPERATION_ERROR.format(
                operation="health check",
                reason=str(e)
            ))
            return {
                "status": "unhealthy",
                "message": f"Erro ao verificar saúde da API: {str(e)}",
                "last_update": datetime.now().isoformat()
            }

    async def update_documents_count(self) -> Optional[int]:
        """Atualiza a contagem de documentos"""
        try:
            from main import supabase
            count = await self.get_documents_count()
            
            # Atualiza estatísticas
            supabase.table("statistics").upsert({
                "key": "documents_count",
                "value": count,
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            return count
        except Exception as e:
            logger.error(MessageTemplate.OPERATION_ERROR.format(
                operation="update documents count",
                reason=str(e)
            ))
            return None

    async def create_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Cria embeddings para um documento"""
        try:
            from main import supabase
            
            logger.info(MessageTemplate.CHUNK_PROCESSING.format(doc_id=document_id))
            
            # Gera embedding
            embedding = self.model.encode(text)
            
            # Salva no Supabase
            result = supabase.table("embeddings").insert({
                "document_id": document_id,
                "embedding": embedding.tolist(),
                "text": text,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            logger.info(MessageTemplate.EMBEDDING_SUCCESS.format(doc_id=document_id))
            
            return {
                "id": result.data[0]["id"],
                "document_id": document_id,
                "vector_dim": len(embedding)
            }
            
        except Exception as e:
            logger.error(MessageTemplate.EMBEDDING_ERROR.format(
                doc_id=document_id,
                error=str(e)
            ))
            raise

    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares baseado em uma query"""
        try:
            from main import supabase
            
            logger.info(MessageTemplate.QUERY_PROCESSING.format(query_text=query))
            
            # Gera embedding da query
            query_embedding = self.model.encode(query)
            
            # Busca similares usando produto escalar
            result = supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding.tolist(),
                    "match_threshold": 0.5,
                    "match_count": limit
                }
            ).execute()
            
            logger.info(MessageTemplate.QUERY_RESULTS.format(count=len(result.data)))
            
            return result.data
            
        except Exception as e:
            logger.error(MessageTemplate.QUERY_ERROR.format(
                query_text=query,
                error=str(e)
            ))
            return []

    async def delete_embeddings(self, document_id: str) -> bool:
        """Remove embeddings de um documento"""
        try:
            from main import supabase
            
            # Remove embeddings
            supabase.table("embeddings").delete().eq("document_id", document_id).execute()
            
            logger.info(MessageTemplate.OPERATION_SUCCESS.format(
                operation=f"delete embeddings for document {document_id}"
            ))
            return True
            
        except Exception as e:
            logger.error(MessageTemplate.VECTOR_STORE_ERROR.format(
                operation=f"delete embeddings for document {document_id}",
                error=str(e)
            ))
            return False

    async def update_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Atualiza embeddings de um documento"""
        try:
            # Remove embeddings antigos
            await self.delete_embeddings(document_id)
            
            # Cria novos embeddings
            return await self.create_embeddings(document_id, text)
            
        except Exception as e:
            logger.error(MessageTemplate.VECTOR_STORE_ERROR.format(
                operation=f"update embeddings for document {document_id}",
                error=str(e)
            ))
            raise 