from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseCluster
import logging

logger = logging.getLogger(__name__)

class ProductionCluster(BaseCluster):
    """Implementação do cluster para ambiente de produção"""
    
    async def get_documents_count(self) -> int:
        """Retorna a contagem real de documentos do Supabase"""
        try:
            from main import supabase
            docs = supabase.table("documents").select("id").execute()
            return len(docs.data)
        except Exception as e:
            logger.error(f"❌ Erro ao obter contagem de documentos: {str(e)}")
            return 0
        
    async def get_embeddings_count(self) -> int:
        """Retorna a contagem real de embeddings do Supabase"""
        try:
            from main import supabase
            embeddings = supabase.table("embeddings").select("id").execute()
            return len(embeddings.data)
        except Exception as e:
            logger.error(f"❌ Erro ao obter contagem de embeddings: {str(e)}")
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
                "environment": self.settings.ENVIRONMENT,
                "timestamp": datetime.now().isoformat(),
                "debug": {
                    "raw_count": docs_count,
                    "stored_count": stored_count,
                    "last_update": stats.data[0]["updated_at"] if stats.data else None
                }
            }
        except Exception as e:
            logger.error(f"❌ Erro no health check: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "environment": self.settings.ENVIRONMENT,
                "timestamp": datetime.now().isoformat()
            }
        
    async def update_documents_count(self) -> Optional[int]:
        """Atualiza a contagem de documentos na tabela de estatísticas"""
        try:
            from main import supabase
            
            # Consulta a quantidade atual de documentos
            count = await self.get_documents_count()
            
            # Atualiza ou insere a contagem na tabela de estatísticas
            stats = {
                "key": "documents_count",
                "value": count,
                "updated_at": datetime.now().isoformat()
            }
            
            # Tenta atualizar primeiro
            response = supabase.table("statistics").upsert(stats).execute()
            
            logger.info(f"✅ Contagem de documentos atualizada: {count}")
            return count
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar contagem de documentos: {str(e)}")
            return None 