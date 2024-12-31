"""Serviço de busca semântica."""

import os
from typing import Any

from supabase import Client, create_client

from backend_rag_ia.constants import (
    DEFAULT_SEARCH_LIMIT,
    ERROR_SUPABASE_CONFIG,
)
from backend_rag_ia.exceptions import (
    DatabaseError,
    EmbeddingError,
    SupabaseError,
)
from backend_rag_ia.utils.logging_config import logger


class SemanticSearch:
    """Serviço de busca semântica."""

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self.supabase = self._init_supabase()
        self.status = {
            "success": False,
            "mode": None,
            "error": None,
        }

    def _init_supabase(self) -> Client:
        """Inicializa cliente do Supabase.

        Returns:
            Cliente do Supabase

        Raises:
            SupabaseError: Se houver erro na configuração
        """
        # Verifica configuração
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.error("Configuração do Supabase incompleta")
            raise SupabaseError(ERROR_SUPABASE_CONFIG)

        try:
            # Inicializa cliente
            supabase = create_client(url, key)
            self._update_status(success=True, mode="local")
            return supabase

        except Exception as e:
            logger.exception("Erro ao conectar ao Supabase: %s", e)
            self._update_status(success=False, mode="local", error=str(e))
            raise SupabaseError from e

    async def search(
        self,
        query: str,
        limit: int = DEFAULT_SEARCH_LIMIT,
        threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Realiza busca semântica.

        Args:
            query: Texto para buscar
            limit: Número máximo de resultados
            threshold: Limiar de similaridade

        Returns:
            Lista de documentos similares

        Raises:
            DatabaseError: Se houver erro na busca
        """
        try:
            # Gera embedding
            embedding = await self._generate_embedding(query)

            # Busca documentos
            results = await self._search_documents(
                embedding=embedding,
                limit=limit,
                threshold=threshold,
            )

            # Retorna resultados
            return results

        except Exception as e:
            logger.exception("Erro na busca: %s", e)
            raise DatabaseError from e

    async def _generate_embedding(self, text: str) -> list[float]:
        """Gera embedding para um texto.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats do embedding

        Raises:
            EmbeddingError: Se houver erro ao gerar embedding
        """
        try:
            # Chama função RPC
            result = await self.supabase.rpc(
                "generate_embedding",
                {"text": text},
            ).execute()

            # Verifica resultado
            if result.data:
                return result.data

            logger.error("Erro ao gerar embedding: resultado vazio")
            raise EmbeddingError("Resultado vazio")

        except Exception as e:
            logger.exception("Erro ao gerar embedding: %s", e)
            raise EmbeddingError from e

    async def _search_documents(
        self,
        embedding: list[float],
        limit: int = DEFAULT_SEARCH_LIMIT,
        threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Busca documentos por similaridade.

        Args:
            embedding: Embedding da query
            limit: Número máximo de resultados
            threshold: Limiar de similaridade

        Returns:
            Lista de documentos similares

        Raises:
            DatabaseError: Se houver erro na busca
        """
        try:
            # Chama função RPC
            result = await self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": embedding,
                    "match_count": limit,
                    "similarity_threshold": threshold,
                },
            ).execute()

            # Verifica resultado
            if result.data:
                return result.data
            return []

        except Exception as e:
            logger.exception("Erro na busca por similaridade: %s", e)
            raise DatabaseError from e

    def _update_status(
        self,
        success: bool,
        mode: str | None = None,
        error: str | None = None,
    ) -> None:
        """Atualiza status do serviço.

        Args:
            success: Se a operação foi bem sucedida
            mode: Modo de operação
            error: Mensagem de erro
        """
        self.status = {
            "success": success,
            "mode": mode,
            "error": error,
        }
