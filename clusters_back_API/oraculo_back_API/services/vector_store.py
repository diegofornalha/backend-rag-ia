"""
Serviço de armazenamento e busca vetorial usando Supabase.
"""
import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from services.supabase_client import supabase
from models.database import Document, DocumentCreate, Embedding, EmbeddingCreate

logger = logging.getLogger(__name__)

class VectorStore:
    """Implementa armazenamento e busca vetorial usando Supabase."""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        batch_size: int = 32
    ) -> None:
        """
        Inicializa o VectorStore.

        Args:
            embedding_model: Nome do modelo de embedding.
            batch_size: Tamanho do lote para operações em batch.
        """
        self.embedding_model = SentenceTransformer(embedding_model)
        self.batch_size = batch_size

    async def add_document(self, content: str, metadata: dict = None) -> Optional[Document]:
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
                content=content,
                metadata=metadata or {},
                document_hash=document_hash
            )
            
            result = supabase.table("documents").insert(doc_data.model_dump()).execute()
            if not result.data:
                raise ValueError("Erro ao inserir documento")
            
            doc_id = result.data[0]["id"]
            
            # Gera e salva embedding
            embedding = self.embedding_model.encode(content)
            embedding_data = EmbeddingCreate(
                document_id=doc_id,
                embedding=embedding.tolist()
            )
            
            result = supabase.table("embeddings").insert(embedding_data.model_dump()).execute()
            if not result.data:
                raise ValueError("Erro ao inserir embedding")
            
            # Atualiza referência do embedding no documento
            embedding_id = result.data[0]["id"]
            supabase.table("documents").update(
                {"embedding_id": embedding_id}
            ).eq("id", doc_id).execute()
            
            return Document.model_validate(result.data[0])
            
        except Exception as e:
            logger.error(f"Erro ao adicionar documento: {e}")
            return None

    async def search(self, query: str, k: int = 4) -> List[Document]:
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
                'match_documents',
                {
                    'query_embedding': query_embedding.tolist(),
                    'match_threshold': 0.7,
                    'match_count': k
                }
            ).execute()
            
            # Converte resultados
            documents = []
            for item in results.data:
                doc = Document.model_validate(item)
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return []

    async def delete_document(self, doc_id: int) -> bool:
        """
        Remove um documento do store.

        Args:
            doc_id: ID do documento.

        Returns:
            bool: True se removido com sucesso.
        """
        try:
            # O embedding será removido automaticamente pela foreign key
            result = supabase.table("documents").delete().eq("id", doc_id).execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Erro ao remover documento: {e}")
            return False 