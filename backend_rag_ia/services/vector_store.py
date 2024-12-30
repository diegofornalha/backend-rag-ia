"""
Serviço de armazenamento e busca vetorial usando Supabase.
"""

import logging

from models.database import Document, DocumentCreate, EmbeddingCreate
from sentence_transformers import SentenceTransformer
from services.supabase_client import supabase

logger = logging.getLogger(__name__)


class VectorStore:
    """Implementa armazenamento e busca vetorial usando Supabase."""

    def __init__(
        self, embedding_model: str = "all-MiniLM-L6-v2", batch_size: int = 32
    ) -> None:
        """
        Inicializa o VectorStore.

        Args:
            embedding_model: Nome do modelo de embedding.
            batch_size: Tamanho do lote para operações em batch.
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.batch_size = batch_size

    async def add_document(
        self, content: str, metadata: dict = None
    ) -> Document | None:
        """
        Adiciona um documento ao store.

        Args:
            content: Conteúdo do documento.
            metadata: Metadados do documento.

        Returns:
            Document: Documento criado ou None se houver erro.
        """
        try:
            # Extrai o document_hash dos metadados
            document_hash = metadata.get("document_hash") if metadata else None

            # Cria documento
            doc_data = DocumentCreate(
                content=content, metadata=metadata or {}, document_hash=document_hash
            )

            result = supabase.table("documents").insert(doc_data.model_dump()).execute()
            if not result.data:
                raise ValueError("Erro ao inserir documento")

            doc_id = result.data[0]["id"]

            # Gera e salva embedding
            embedding = self.embedding_model.encode(content)
            embedding_data = EmbeddingCreate(
                document_id=doc_id, embedding=embedding.tolist()
            )

            result = (
                supabase.table("embeddings")
                .insert(embedding_data.model_dump())
                .execute()
            )
            if not result.data:
                raise ValueError("Erro ao inserir embedding")

            # Atualiza referência do embedding no documento
            embedding_id = result.data[0]["id"]
            supabase.table("documents").update({"embedding_id": embedding_id}).eq(
                "id", doc_id
            ).execute()

            return Document.model_validate(result.data[0])

        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            return None

    async def search(self, query: str, k: int = 4) -> list[Document]:
        """
        Busca documentos similares à query.

        Args:
            query: Texto da busca.
            k: Número de resultados.

        Returns:
            List[Document]: Lista de documentos similares.
        """
        try:
            # Gera embedding da query
            query_embedding = self.embedding_model.encode(query)

            # Busca documentos similares
            results = supabase.rpc(
                "match_documents",
                {"query_embedding": query_embedding.tolist(), "match_count": k},
            ).execute()

            if not results.data:
                return []

            return [Document.model_validate(doc) for doc in results.data]

        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []

    async def delete_document(self, doc_id: str) -> bool:
        """
        Remove um documento e seu embedding.

        Args:
            doc_id: ID do documento.

        Returns:
            bool: True se removido com sucesso, False caso contrário.
        """
        try:
            # Busca o documento para obter o embedding_id
            doc = supabase.table("documents").select("*").eq("id", doc_id).execute()
            if not doc.data:
                return False

            embedding_id = doc.data[0].get("embedding_id")

            # Remove o embedding se existir
            if embedding_id:
                supabase.table("embeddings").delete().eq("id", embedding_id).execute()

            # Remove o documento
            result = supabase.table("documents").delete().eq("id", doc_id).execute()
            return bool(result.data)

        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return False

    async def list_documents(self, skip: int = 0, limit: int = 10) -> list[Document]:
        """
        Lista documentos com paginação.

        Args:
            skip: Número de documentos para pular.
            limit: Número máximo de documentos para retornar.

        Returns:
            List[Document]: Lista de documentos.
        """
        try:
            result = (
                supabase.table("documents")
                .select("*")
                .range(skip, skip + limit - 1)
                .execute()
            )
            if not result.data:
                return []
            return [Document.model_validate(doc) for doc in result.data]
        except Exception as e:
            logger.error(f"Erro ao listar documentos: {e}")
            return []

    async def get_document(self, doc_id: str) -> Document | None:
        """
        Busca um documento pelo ID.

        Args:
            doc_id: ID do documento.

        Returns:
            Optional[Document]: Documento encontrado ou None.
        """
        try:
            result = supabase.table("documents").select("*").eq("id", doc_id).execute()
            if not result.data:
                return None
            return Document.model_validate(result.data[0])
        except Exception as e:
            logger.error(f"Erro ao buscar documento: {e}")
            return None

    async def update_document(
        self, doc_id: str, content: str, metadata: dict = None
    ) -> bool:
        """
        Atualiza um documento existente.

        Args:
            doc_id: ID do documento.
            content: Novo conteúdo.
            metadata: Novos metadados.

        Returns:
            bool: True se atualizado com sucesso.
        """
        try:
            # Verifica se o documento existe
            doc = await self.get_document(doc_id)
            if not doc:
                return False

            # Atualiza o documento
            doc_data = {"content": content, "metadata": metadata or {}}

            # Gera novo embedding
            embedding = self.embedding_model.encode(content)

            # Atualiza embedding existente
            embedding_result = (
                supabase.table("embeddings")
                .update({"embedding": embedding.tolist()})
                .eq("document_id", doc_id)
                .execute()
            )

            if not embedding_result.data:
                raise ValueError("Erro ao atualizar embedding")

            # Atualiza documento
            result = (
                supabase.table("documents").update(doc_data).eq("id", doc_id).execute()
            )
            return bool(result.data)

        except Exception as e:
            logger.error(f"Erro ao atualizar documento: {e}")
            return False

    async def get_documents_history(self, hours: int = 24) -> list[dict]:
        """
        Busca o histórico de alterações nos documentos.

        Args:
            hours: Número de horas para buscar o histórico.

        Returns:
            List[Dict]: Lista de alterações com detalhes.
        """
        try:
            result = supabase.rpc(
                "get_document_changes_history", {"last_n_hours": hours}
            ).execute()

            if not result.data:
                return []

            return result.data

        except Exception as e:
            logger.error(f"Erro ao buscar histórico: {e}")
            return []

    async def get_statistics(self) -> list[dict]:
        """
        Busca estatísticas do sistema.

        Returns:
            List[Dict]: Lista de estatísticas com seus valores e timestamps.
        """
        try:
            result = supabase.table("statistics").select("*").execute()

            if not result.data:
                return []

            return result.data

        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return []

    async def count_documents(self) -> int:
        """
        Conta o total de documentos no sistema.

        Returns:
            int: Número total de documentos.
        """
        try:
            # Busca o valor atual da estatística
            result = (
                supabase.table("statistics")
                .select("value")
                .eq("key", "documents_count")
                .execute()
            )

            if result.data:
                return result.data[0]["value"]

            # Se não encontrar na tabela statistics, conta diretamente
            result = (
                supabase.table("documents").select("count", count="exact").execute()
            )
            return result.count or 0

        except Exception as e:
            logger.error(f"Erro ao contar documentos: {e}")
            return 0

    async def health_check(self) -> bool:
        """
        Verifica a saúde do sistema.

        Returns:
            bool: True se saudável, False caso contrário.
        """
        try:
            # Tenta fazer uma consulta simples
            result = (
                supabase.table("documents").select("count", count="exact").execute()
            )
            return True
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            return False
