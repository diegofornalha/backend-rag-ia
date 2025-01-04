"""Implementa configuração do cliente Supabase com suporte a diferentes tipos de autenticação."""

from typing import Any

from supabase import Client, create_client

from .env_config import config


class SupabaseConfig:
    """Gerencia configuração do Supabase.

    Esta classe gerencia a configuração e inicialização do cliente Supabase,
    fornecendo métodos para autenticação e operações com embeddings.
    """

    def __init__(self, require_service_key: bool = True):
        """Inicializa o cliente Supabase.

        Parameters
        ----------
        require_service_key : bool, optional
            Se True, usa apenas service_key; se False, pode usar anon_key.
            Por padrão é True.

        Raises
        ------
        ValueError
            Se as configurações do Supabase forem inválidas ou incompletas.

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
        """Gera embedding para o texto usando função RPC do Supabase.

        Parameters
        ----------
        text : str
            Texto para gerar embedding.

        Returns
        -------
        list[float]
            Lista de embeddings ou lista vazia em caso de erro.

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
        """Busca documentos similares usando função RPC do Supabase.

        Parameters
        ----------
        query_embedding : list[float]
            Embedding da consulta.
        match_threshold : float, optional
            Limite mínimo de similaridade, por padrão 0.7.
        match_count : int, optional
            Número máximo de documentos a retornar, por padrão 10.

        Returns
        -------
        list[dict[Any, Any]]
            Lista de documentos encontrados ou lista vazia em caso de erro.

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
        """Realiza busca semântica completa.

        Parameters
        ----------
        query : str
            Texto da consulta.

        Returns
        -------
        list[dict[Any, Any]]
            Lista de documentos encontrados ou lista vazia em caso de erro.

        """
        try:
            embedding = self.generate_embedding(query)
            if not embedding:
                return []

            return self.match_documents(embedding)
        except Exception as e:
            print(f"❌ Erro na busca semântica: {e}")
            return []
