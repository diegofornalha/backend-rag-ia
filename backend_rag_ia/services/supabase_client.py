"""Módulo para interação com o Supabase.

Este módulo fornece funcionalidades para interagir com o banco de dados
Supabase, incluindo operações de CRUD e gerenciamento de documentos.
"""

from typing import Any

from supabase import create_client

from backend_rag_ia.config.env_config import get_env_config


class SupabaseClient:
    """Cliente para interação com o Supabase.

    Esta classe fornece métodos para interagir com o banco de dados
    Supabase, incluindo operações de CRUD e gerenciamento de documentos.

    Attributes
    ----------
    client : supabase.Client
        Cliente Supabase configurado.
    table_name : str
        Nome da tabela de documentos.

    """

    def __init__(self, table_name: str = "documents") -> None:
        """Inicializa o cliente.

        Parameters
        ----------
        table_name : str, optional
            Nome da tabela de documentos, por padrão "documents".

        """
        env_config = get_env_config()
        self.client = create_client(
            env_config.supabase_url,
            env_config.supabase_key
        )
        self.table_name = table_name

    def insert_document(self, document: dict[str, Any]) -> dict[str, Any]:
        """Insere um documento no banco de dados.

        Parameters
        ----------
        document : dict[str, Any]
            Documento a ser inserido.

        Returns
        -------
        dict[str, Any]
            Documento inserido com ID gerado.

        """
        result = self.client.table(self.table_name).insert(document).execute()
        return result.data[0] if result.data else {}

    def get_document(self, document_id: str) -> dict[str, Any]:
        """Obtém um documento do banco de dados.

        Parameters
        ----------
        document_id : str
            ID do documento.

        Returns
        -------
        dict[str, Any]
            Documento encontrado ou dicionário vazio.

        """
        result = (
            self.client.table(self.table_name)
            .select("*")
            .eq("id", document_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def update_document(
        self,
        document_id: str,
        updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Atualiza um documento no banco de dados.

        Parameters
        ----------
        document_id : str
            ID do documento.
        updates : dict[str, Any]
            Atualizações a serem aplicadas.

        Returns
        -------
        dict[str, Any]
            Documento atualizado.

        """
        result = (
            self.client.table(self.table_name)
            .update(updates)
            .eq("id", document_id)
            .execute()
        )
        return result.data[0] if result.data else {}

    def delete_document(self, document_id: str) -> bool:
        """Remove um documento do banco de dados.

        Parameters
        ----------
        document_id : str
            ID do documento.

        Returns
        -------
        bool
            True se o documento foi removido, False caso contrário.

        """
        result = (
            self.client.table(self.table_name)
            .delete()
            .eq("id", document_id)
            .execute()
        )
        return bool(result.data)

    def list_documents(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """Lista documentos do banco de dados.

        Parameters
        ----------
        limit : int, optional
            Número máximo de documentos, por padrão 100.
        offset : int, optional
            Deslocamento para paginação, por padrão 0.

        Returns
        -------
        list[dict[str, Any]]
            Lista de documentos encontrados.

        """
        result = (
            self.client.table(self.table_name)
            .select("*")
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data if result.data else []

    def search_documents(self, query: str) -> list[dict[str, Any]]:
        """Busca documentos no banco de dados.

        Parameters
        ----------
        query : str
            Texto para busca.

        Returns
        -------
        list[dict[str, Any]]
            Lista de documentos encontrados.

        """
        result = (
            self.client.table(self.table_name)
            .select("*")
            .textSearch("content", query)
            .execute()
        )
        return result.data if result.data else []
