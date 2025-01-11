import os
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer
from supabase import Client, create_client


class VectorStore:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase: Client = create_client(url, key)
        self.model = SentenceTransformer(os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2"))
        self.collection = os.getenv("VECTOR_STORE_COLLECTION", "embeddings")
        self._init_db()

    def _init_db(self):
        # Supabase já tem pgvector habilitado por padrão
        # Criar tabela se não existir
        self.supabase.rpc(
            "create_embeddings_table",
            {
                "table_name": self.collection,
                "embedding_dimension": 384,  # Dimensão do modelo all-MiniLM-L6-v2
            },
        ).execute()

    async def store_content(self, content: str, metadata: dict[str, Any] = None) -> list[float]:
        # Gerar embedding
        embedding = self.model.encode(content)

        # Armazenar no Supabase
        self.supabase.table(self.collection).insert(
            {"content": content, "embedding": embedding.tolist(), "metadata": metadata or {}}
        ).execute()

        return embedding.tolist()

    async def search_similar(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        # Gerar embedding da query
        query_embedding = self.model.encode(query)

        # Buscar conteúdo similar usando a função match_documents do Supabase
        response = self.supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding.tolist(),
                "match_threshold": 0.5,
                "match_count": limit,
                "table_name": self.collection,
            },
        ).execute()

        results = []
        for item in response.data:
            results.append(
                {
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "similarity": float(item["similarity"]),
                }
            )

        return results
