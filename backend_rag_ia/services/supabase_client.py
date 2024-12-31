"""Cliente Supabase para operações no banco de dados."""

import os
from typing import Any

from postgrest.exceptions import APIError
from supabase import create_client

from backend_rag_ia.constants import (
    ERROR_SUPABASE_CONFIG,
    ERROR_SUPABASE_CONNECT,
)
from backend_rag_ia.exceptions import (
    DatabaseError,
    EmbeddingError,
    SupabaseError,
)
from backend_rag_ia.utils.logging_config import logger


class SupabaseClient:
    """Cliente para operações no Supabase."""

    def __init__(self) -> None:
        """Inicializa o cliente.

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
            self.client = create_client(url, key)

        except Exception as e:
            logger.exception("Erro ao conectar ao Supabase: %s", e)
            raise SupabaseError(ERROR_SUPABASE_CONNECT) from e

    async def insert(self, table: str, data: dict[str, Any]) -> dict[str, Any]:
        """Insere um registro na tabela.

        Args:
            table: Nome da tabela
            data: Dados para inserir

        Returns:
            Registro inserido

        Raises:
            DatabaseError: Se houver erro na inserção
        """
        try:
            result = await self.client.table(table).insert(data).execute()
            return result.data[0]

        except APIError as e:
            logger.exception("Erro ao inserir no Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao inserir no Supabase: %s", e)
            raise DatabaseError from e

    async def update(
        self,
        table: str,
        id_: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Atualiza um registro na tabela.

        Args:
            table: Nome da tabela
            id_: ID do registro
            data: Dados para atualizar

        Returns:
            Registro atualizado

        Raises:
            DatabaseError: Se houver erro na atualização
        """
        try:
            result = await self.client.table(table).update(data).eq("id", id_).execute()
            return result.data[0]

        except APIError as e:
            logger.exception("Erro ao atualizar no Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao atualizar no Supabase: %s", e)
            raise DatabaseError from e

    async def delete(self, table: str, id_: str) -> dict[str, Any]:
        """Remove um registro da tabela.

        Args:
            table: Nome da tabela
            id_: ID do registro

        Returns:
            Registro removido

        Raises:
            DatabaseError: Se houver erro na remoção
        """
        try:
            result = await self.client.table(table).delete().eq("id", id_).execute()
            return result.data[0]

        except APIError as e:
            logger.exception("Erro ao remover do Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao remover do Supabase: %s", e)
            raise DatabaseError from e

    async def get(self, table: str, id_: str) -> dict[str, Any] | None:
        """Busca um registro pelo ID.

        Args:
            table: Nome da tabela
            id_: ID do registro

        Returns:
            Registro encontrado ou None

        Raises:
            DatabaseError: Se houver erro na busca
        """
        try:
            result = await self.client.table(table).select("*").eq("id", id_).execute()
            if result.data:
                return result.data[0]
            return None

        except APIError as e:
            logger.exception("Erro ao buscar no Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao buscar no Supabase: %s", e)
            raise DatabaseError from e

    async def list(
        self,
        table: str,
        skip: int = 0,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Lista registros com paginação.

        Args:
            table: Nome da tabela
            skip: Número de registros para pular
            limit: Número máximo de registros

        Returns:
            Lista de registros

        Raises:
            DatabaseError: Se houver erro na listagem
        """
        try:
            result = await self.client.table(table).select("*").range(skip, skip + limit - 1).execute()
            if result.data:
                return result.data
            return []

        except APIError as e:
            logger.exception("Erro ao listar no Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao listar no Supabase: %s", e)
            raise DatabaseError from e

    async def count(self, table: str) -> int:
        """Conta registros na tabela.

        Args:
            table: Nome da tabela

        Returns:
            Total de registros

        Raises:
            DatabaseError: Se houver erro na contagem
        """
        try:
            result = await self.client.table(table).select("count", count="exact").execute()
            if result.count is not None:
                return result.count
            return 0

        except APIError as e:
            logger.exception("Erro ao contar no Supabase: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro ao contar no Supabase: %s", e)
            raise DatabaseError from e

    async def search(
        self,
        query_embedding: list[float],
        k: int = 4,
        threshold: float = 0.5,
    ) -> list[dict[str, Any]]:
        """Busca registros por similaridade.

        Args:
            query_embedding: Embedding da query
            k: Número de resultados
            threshold: Limiar de similaridade

        Returns:
            Lista de registros similares

        Raises:
            DatabaseError: Se houver erro na busca
        """
        try:
            result = await self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": k,
                    "similarity_threshold": threshold,
                },
            ).execute()
            if result.data:
                return result.data
            return []

        except APIError as e:
            logger.exception("Erro na busca por similaridade: %s", e)
            raise DatabaseError from e

        except Exception as e:
            logger.exception("Erro na busca por similaridade: %s", e)
            raise DatabaseError from e

    async def generate_embedding(self, text: str) -> list[float]:
        """Gera embedding para um texto.

        Args:
            text: Texto para gerar embedding

        Returns:
            Lista de floats do embedding

        Raises:
            EmbeddingError: Se houver erro ao gerar embedding
        """
        try:
            result = await self.client.rpc(
                "generate_embedding",
                {"text": text},
            ).execute()
            if result.data:
                return result.data

            logger.error("Erro ao gerar embedding: resultado vazio")
            raise EmbeddingError("Resultado vazio")

        except APIError as e:
            logger.exception("Erro ao gerar embedding: %s", e)
            raise EmbeddingError from e

        except Exception as e:
            logger.exception("Erro ao gerar embedding: %s", e)
            raise EmbeddingError from e
