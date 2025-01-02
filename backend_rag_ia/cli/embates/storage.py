"""
Gerenciamento de armazenamento de embates no Supabase.
"""

from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client, Client
from backend_rag_ia.config.settings import get_settings
from backend_rag_ia.services.semantic_search import SemanticSearchManager
from backend_rag_ia.utils.logging_config import logger
from .models import Embate

settings = get_settings()

class SupabaseStorage:
    """Gerencia armazenamento no Supabase."""
    
    def __init__(self):
        """Inicializa o cliente Supabase e o gerenciador semântico."""
        self.client: Client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        self.semantic_manager = SemanticSearchManager()
        self.logger = logger
    
    async def save_embate(self, embate: Embate) -> Dict[str, Any]:
        """
        Salva um embate no Supabase com embedding.
        
        Args:
            embate: Instância de Embate para salvar
            
        Returns:
            Dict com resultado da operação
        """
        try:
            # Gera embedding do conteúdo
            embedding = self.semantic_manager._get_embedding(
                f"{embate.titulo} {embate.contexto}"
            )
            
            # Prepara metadados
            metadata = embate.metadata or {}
            metadata.update({
                "data_criacao": datetime.now().isoformat(),
                "ultima_atualizacao": datetime.now().isoformat(),
                "status": embate.status,
                "tipo": embate.tipo
            })
            
            # Salva via RPC
            result = await self.client.rpc(
                "save_embate_with_embedding",
                {
                    "embate": embate.dict(),
                    "embedding": embedding,
                    "metadata": metadata
                }
            ).execute()
            
            self.logger.info(
                "Embate salvo com sucesso",
                extra={"arquivo": embate.arquivo}
            )
            return result.data
            
        except Exception as e:
            self.logger.error(
                "Erro ao salvar embate",
                extra={"error": str(e), "arquivo": embate.arquivo},
                exc_info=True
            )
            raise
    
    async def update_embate(self, embate_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Atualiza um embate existente.
        
        Args:
            embate_id: ID do embate
            updates: Dicionário com atualizações
            
        Returns:
            Dict com resultado da operação
        """
        try:
            updates["metadata"] = updates.get("metadata", {})
            updates["metadata"]["ultima_atualizacao"] = datetime.now().isoformat()
            
            result = await self.client.rpc(
                "update_embate",
                {"embate_id": embate_id, "updates": updates}
            ).execute()
            
            self.logger.info(
                "Embate atualizado com sucesso",
                extra={"embate_id": embate_id}
            )
            return result.data
            
        except Exception as e:
            self.logger.error(
                "Erro ao atualizar embate",
                extra={"error": str(e), "embate_id": embate_id},
                exc_info=True
            )
            raise
    
    async def search_embates(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca embates usando similaridade semântica.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Lista de embates encontrados
        """
        try:
            # Gera embedding da query
            embedding = self.semantic_manager._get_embedding(query)
            
            # Busca via RPC
            result = await self.client.rpc(
                "search_embates",
                {"query_embedding": embedding, "match_threshold": 0.8}
            ).execute()
            
            self.logger.info(
                "Busca realizada com sucesso",
                extra={"query": query}
            )
            return result.data
            
        except Exception as e:
            self.logger.error(
                "Erro ao buscar embates",
                extra={"error": str(e), "query": query},
                exc_info=True
            )
            raise
    
    async def export_embates(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Exporta embates com filtros.
        
        Args:
            filters: Dicionário com filtros
            
        Returns:
            Lista de embates exportados
        """
        try:
            result = await self.client.rpc(
                "export_embates",
                {"filters": filters}
            ).execute()
            
            self.logger.info(
                "Embates exportados com sucesso",
                extra={"filters": filters}
            )
            return result.data
            
        except Exception as e:
            self.logger.error(
                "Erro ao exportar embates",
                extra={"error": str(e), "filters": filters},
                exc_info=True
            )
            raise 