"""Módulo para interagir com o Supabase Vector Store.

Este módulo fornece uma classe para gerenciar documentos no Supabase Vector Store,
incluindo operações CRUD e busca por similaridade.
"""

import logging
import os
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

logger = logging.getLogger(__name__)


class VectorStore:
    """Classe para interagir com o Supabase Vector Store.

    Esta classe fornece métodos para gerenciar documentos no Supabase Vector Store,
    incluindo inserção, atualização, remoção e busca por similaridade.
    """

    def __init__(self) -> None:
        """Inicializa o cliente Supabase.

        Raises
        ------
        ValueError
            Se as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não estiverem definidas.

        """
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")

        self.supabase_client: Client = create_client(supabase_url, supabase_key)

    def insert_document(self, titulo: str, conteudo: dict[str, Any], document_hash: str, version_key: str) -> str:
        """Insere um documento no Supabase.

        Parameters
        ----------
        titulo : str
            Título do documento.
        conteudo : dict[str, Any]
            Conteúdo do documento.
        document_hash : str
            Hash do documento.
        version_key : str
            Chave de versão.

        Returns
        -------
        str
            ID do documento inserido.

        Raises
        ------
        ValueError
            Se houver erro ao inserir o documento.
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.table('rag.01_base_conhecimento_regras_geral').insert({
                'titulo': titulo,
                'conteudo': conteudo,
                'document_hash': document_hash,
                'version_key': version_key
            }).execute()

            if not response.data:
                raise ValueError("Erro ao inserir documento: resposta vazia")

            return response.data[0]['id']

        except Exception as e:
            logger.error("Erro ao inserir documento", extra={"error": str(e)})
            raise

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        """Obtém um documento do Supabase.

        Parameters
        ----------
        document_id : str
            ID do documento.

        Returns
        -------
        dict[str, Any] | None
            Documento encontrado ou None se não encontrado.

        Raises
        ------
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.table('rag.01_base_conhecimento_regras_geral').select('*').eq('id', document_id).execute()
            return response.data[0] if response.data else None

        except Exception as e:
            logger.error("Erro ao obter documento", extra={"error": str(e)})
            raise

    def update_document(self, document_id: str, titulo: str, conteudo: dict[str, Any], document_hash: str, version_key: str) -> None:
        """Atualiza um documento no Supabase.

        Parameters
        ----------
        document_id : str
            ID do documento.
        titulo : str
            Título do documento.
        conteudo : dict[str, Any]
            Conteúdo do documento.
        document_hash : str
            Hash do documento.
        version_key : str
            Chave de versão.

        Raises
        ------
        ValueError
            Se houver erro ao atualizar o documento.
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.table('rag.01_base_conhecimento_regras_geral').update({
                'titulo': titulo,
                'conteudo': conteudo,
                'document_hash': document_hash,
                'version_key': version_key
            }).eq('id', document_id).execute()

            if not response.data:
                raise ValueError("Erro ao atualizar documento: resposta vazia")

        except Exception as e:
            logger.error("Erro ao atualizar documento", extra={"error": str(e)})
            raise

    def delete_document(self, document_id: str) -> None:
        """Remove um documento do Supabase.

        Parameters
        ----------
        document_id : str
            ID do documento.

        Raises
        ------
        ValueError
            Se houver erro ao deletar o documento.
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.table('rag.01_base_conhecimento_regras_geral').delete().eq('id', document_id).execute()
            if not response.data:
                raise ValueError("Erro ao deletar documento: resposta vazia")

        except Exception as e:
            logger.error("Erro ao deletar documento", extra={"error": str(e)})
            raise

    def list_documents(self) -> list[dict[str, Any]]:
        """Lista todos os documentos do Supabase.

        Returns
        -------
        list[dict[str, Any]]
            Lista de documentos.

        Raises
        ------
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.table('rag.01_base_conhecimento_regras_geral').select('*').execute()
            return response.data if response.data else []

        except Exception as e:
            logger.error("Erro ao listar documentos", extra={"error": str(e)})
            raise

    def search_similar_documents(self, query_embedding: list[float], match_count: int = 5) -> list[tuple[dict[str, Any], float]]:
        """Busca documentos similares usando o embedding da query.

        Parameters
        ----------
        query_embedding : list[float]
            Embedding da query.
        match_count : int, optional
            Número de documentos para retornar, by default 5.

        Returns
        -------
        list[tuple[dict[str, Any], float]]
            Lista de tuplas (documento, similaridade).

        Raises
        ------
        Exception
            Se ocorrer um erro durante a operação.

        """
        try:
            response = self.supabase_client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_count': match_count
                }
            ).execute()

            if not response.data:
                return []

            results = []
            for item in response.data:
                doc = item.get('document', {})
                similarity = item.get('similarity', 0.0)
                results.append((doc, similarity))

            return results

        except Exception as e:
            logger.error("Erro ao buscar documentos similares", extra={"error": str(e)})
            raise
