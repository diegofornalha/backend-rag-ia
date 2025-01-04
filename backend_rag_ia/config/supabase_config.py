"""
Configuração do cliente Supabase com suporte a diferentes tipos de autenticação.
"""

from typing import Any

from supabase import Client, create_client

from .env_config import config


class SupabaseConfig:
    """Gerenciador de configuração do Supabase."""
    
    def __init__(self, require_service_key: bool = True):
        """
        Inicializa o cliente Supabase.
        
        Args:
            require_service_key: Se True, usa apenas service_key; se False, pode usar anon_key
        """
        if not config.validate():
            raise ValueError("Configurações do Supabase inválidas ou incompletas")
            
        self.url: str = config.supabase.url
        self.key: str = config.get_supabase_key(require_service_key)
        
        if not self.key:
            key_type = "service_key" if require_service_key else "anon_key ou service_key"
            raise ValueError(f"Chave do Supabase ({key_type}) não encontrada")
            
        self.client: Client = create_client(self.url, self.key)

    def generate_embedding(self, text: str) -> list[float]:
        """
        Gera embedding para o texto usando função RPC do Supabase.
        
        Args:
            text: Texto para gerar embedding
            
        Returns:
            List[float]: Lista de embeddings ou lista vazia em caso de erro
        """
        try:
            response = self.client.rpc(
                "generate_embedding",
                {"input_text": text}
            ).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {e}")
            return []

    def match_documents(
        self,
        query_embedding: list[float],
        match_threshold: float = 0.7,
        match_count: int = 10
    ) -> list[dict[Any, Any]]:
        """
        Busca documentos similares usando função RPC do Supabase.
        
        Args:
            query_embedding: Embedding da consulta
            match_threshold: Limite mínimo de similaridade
            match_count: Número máximo de documentos a retornar
            
        Returns:
            List[Dict]: Lista de documentos encontrados ou lista vazia em caso de erro
        """
        try:
            response = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count
                }
            ).execute()
            return response.data
        except Exception as e:
            print(f"❌ Erro na busca de documentos: {e}")
            return []

    def search_documents(self, query: str) -> list[dict[Any, Any]]:
        """
        Realiza busca semântica completa.
        
        Args:
            query: Texto da consulta
            
        Returns:
            List[Dict]: Lista de documentos encontrados ou lista vazia em caso de erro
        """
        try:
            embedding = self.generate_embedding(query)
            if not embedding:
                return []
            
            return self.match_documents(embedding)
        except Exception as e:
            print(f"❌ Erro na busca semântica: {e}")
            return [] 