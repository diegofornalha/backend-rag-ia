"""Serviço de armazenamento de vetores."""

from typing import Any, List
from supabase import Client as SupabaseClient
from sentence_transformers import SentenceTransformer

class VectorStore:
    """Armazenamento de documentos com embeddings."""

    def __init__(self, supabase_client: SupabaseClient) -> None:
        """Inicializa o armazenamento.

        Args:
            supabase_client: Cliente do Supabase
        """
        self.supabase_client = supabase_client
        self.table = "documents"

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Cria embeddings para uma lista de textos usando o modelo all-MiniLM-L6-v2.

        Args:
            texts: Lista de textos para gerar embeddings

        Returns:
            Lista de embeddings
        """
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = model.encode(texts)
        return embeddings.tolist()

    def insert_documents(self, documents: List[dict[str, Any]]) -> None:
        """Insere documentos no Supabase com seus embeddings.

        Args:
            documents: Lista de documentos para inserir
        """
        for doc in documents:
            embedding = self.create_embeddings([doc['content']])[0]
            doc['embedding'] = embedding
            self.supabase_client.table('documents').insert(doc).execute()

    def search_documents(self, query: str, match_count: int = 3) -> List[dict[str, Any]]:
        """Realiza uma busca semântica por documentos similares à query.

        Args:
            query: Texto para buscar
            match_count: Número máximo de resultados

        Returns:
            Lista de documentos similares
        """
        query_embedding = self.create_embeddings([query])[0]

        rpc_response = self.supabase_client.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_count': match_count
            }
        ).execute()

        return rpc_response.data

    def delete_document(self, document_id: str) -> None:
        """Remove um documento específico do Supabase.

        Args:
            document_id: ID do documento para remover
        """
        self.supabase_client.table('documents').delete().eq('id', document_id).execute()

    def update_document(self, document_id: str, new_content: str) -> None:
        """Atualiza o conteúdo e embedding de um documento existente.

        Args:
            document_id: ID do documento para atualizar
            new_content: Novo conteúdo do documento
        """
        new_embedding = self.create_embeddings([new_content])[0]

        self.supabase_client.table('documents').update({
            'content': new_content,
            'embedding': new_embedding
        }).eq('id', document_id).execute()

    def get_document(self, document_id: str) -> dict[str, Any]:
        """Recupera um documento específico do Supabase.

        Args:
            document_id: ID do documento para recuperar

        Returns:
            Documento encontrado ou None
        """
        response = self.supabase_client.table('documents').select('*').eq('id', document_id).execute()
        return response.data[0] if response.data else None

    def list_documents(self) -> List[dict[str, Any]]:
        """Lista todos os documentos armazenados no Supabase.

        Returns:
            Lista de documentos
        """
        response = self.supabase_client.table('documents').select('*').execute()
        return response.data

    def clear_documents(self) -> None:
        """Remove todos os documentos do Supabase."""
        self.supabase_client.table('documents').delete().neq('id', '').execute()
