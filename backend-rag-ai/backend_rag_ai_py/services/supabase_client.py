"""Cliente Supabase para operações no banco de dados."""

from typing import Any, Dict, List, Optional

from supabase import Client, create_client


class SupabaseClient:
    """Cliente para operações no Supabase."""

    def __init__(self, url: str, key: str):
        """
        Inicializa o cliente.

        Args:
            url: URL do projeto Supabase
            key: Chave de API do Supabase
        """
        self.client = create_client(url, key)

    def _ensure_schema(self, table: str) -> str:
        """
        Garante que a tabela use o schema rag.

        Args:
            table: Nome da tabela

        Returns:
            Nome da tabela com schema
        """
        if not table.startswith("rag."):
            table = f"rag.{table}"
        return table

    async def insert(self, table: str, data: dict) -> dict:
        """
        Insere dados em uma tabela.

        Args:
            table: Nome da tabela
            data: Dados a inserir

        Returns:
            Dados inseridos
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).insert(data).execute()
        return result.data[0]

    async def update(self, table: str, id_: str, data: dict) -> dict:
        """
        Atualiza dados em uma tabela.

        Args:
            table: Nome da tabela
            id_: ID do registro
            data: Dados a atualizar

        Returns:
            Dados atualizados
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).update(data).eq("id", id_).execute()
        return result.data[0]

    async def delete(self, table: str, id_: str) -> None:
        """
        Remove dados de uma tabela.

        Args:
            table: Nome da tabela
            id_: ID do registro
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).delete().eq("id", id_).execute()

    async def get(self, table: str, id_: str) -> dict | None:
        """
        Busca dados em uma tabela.

        Args:
            table: Nome da tabela
            id_: ID do registro

        Returns:
            Dados encontrados ou None
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).select("*").eq("id", id_).execute()
        return result.data[0] if result.data else None

    async def list(self, table: str, skip: int = 0, limit: int = 100) -> list[dict]:
        """
        Lista dados de uma tabela.

        Args:
            table: Nome da tabela
            skip: Registros a pular
            limit: Limite de registros

        Returns:
            Lista de dados
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).select("*").range(skip, skip + limit - 1).execute()
        return result.data

    async def count(self, table: str) -> int:
        """
        Conta registros em uma tabela.

        Args:
            table: Nome da tabela

        Returns:
            Número de registros
        """
        table = self._ensure_schema(table)
        result = await self.client.table(table).select("count", count="exact").execute()
        return result.count
