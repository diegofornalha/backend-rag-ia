"""Serviço de busca semântica."""

import os
import hashlib
from typing import Any, Dict, List, Optional
from supabase import Client, create_client
import json
from sentence_transformers import SentenceTransformer

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
from .llm_manager import LLMManager

class SemanticSearchManager:
    """Serviço de busca semântica com RAG."""

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self.supabase = self._init_supabase()
        self.llm_manager = LLMManager()
        self.embedding_cache = {}
        self.cache_dir = os.getenv("LANGCHAIN_CACHE_DIR", ".cache/embeddings")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def _init_supabase(self) -> Client:
        """Inicializa cliente do Supabase."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            logger.error("Configuração do Supabase incompleta")
            raise SupabaseError(ERROR_SUPABASE_CONFIG)

        try:
            return create_client(url, key)
        except Exception as e:
            logger.exception("Erro ao conectar ao Supabase: %s", e)
            raise SupabaseError from e

    def search(
        self,
        query: str,
        limit: int = DEFAULT_SEARCH_LIMIT,
        threshold: float = 0.5,
    ) -> Dict[str, Any]:
        """Realiza busca semântica."""
        try:
            # Temporariamente usando apenas busca textual
            results = self._text_search(query, limit)
            
            if not results:
                logger.warning("Nenhum resultado encontrado")
                return {
                    "answer": "Nenhum documento relevante encontrado",
                    "results": []
                }
                
            # Reordena resultados usando LLM
            reranked = self.llm_manager.rerank_results(
                query=query,
                results=results,
                top_k=min(5, len(results))
            )
            
            # Processa com LLM
            processed = self.llm_manager.process_results(
                query=query,
                results=reranked
            )
            
            return {
                **processed,
                "total_results": len(results),
                "reranked_results": len(reranked)
            }

        except Exception as e:
            logger.warning("Erro na busca semântica: %s", e)
            return {
                "answer": f"Erro na busca: {str(e)}",
                "results": []
            }

    def _semantic_search(
        self,
        query: str,
        limit: int,
        threshold: float,
    ) -> List[Dict[str, Any]]:
        """Realiza busca semântica."""
        try:
            # Gera ou busca embedding em cache
            embedding = self._get_embedding(query)
            
            if not embedding:
                return []
                
            # Busca documentos similares
            return self._search_documents(embedding, limit, threshold)
            
        except Exception as e:
            logger.warning("Erro na busca semântica: %s", e)
            return []

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Gera ou recupera embedding do cache."""
        # Gera chave de cache
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Verifica cache em memória
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
            
        # Verifica cache em disco
        if os.path.exists(cache_file):
            with open(cache_file) as f:
                embedding = json.load(f)
                self.embedding_cache[cache_key] = embedding
                return embedding
                
        try:
            # Gera novo embedding localmente
            embedding = self.model.encode(text).tolist()
                
            # Salva em cache
            self.embedding_cache[cache_key] = embedding
            with open(cache_file, "w") as f:
                json.dump(embedding, f)
                
            return embedding
            
        except Exception as e:
            logger.exception("Erro ao gerar embedding: %s", e)
            return None

    def _search_documents(
        self,
        embedding: List[float],
        limit: int = DEFAULT_SEARCH_LIMIT,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Busca documentos por similaridade."""
        try:
            # Converte embedding para array de double precision
            embedding_array = [float(x) for x in embedding]
            
            result = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": embedding_array,
                    "match_count": limit,
                    "match_threshold": threshold
                }
            ).execute()

            if hasattr(result, 'data'):
                return result.data or []
            return result or []

        except Exception as e:
            logger.exception("Erro na busca por similaridade: %s", e)
            raise DatabaseError from e

    def _text_search(
        self,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Realiza busca textual como fallback."""
        try:
            # Primeiro tenta buscar todos os documentos
            response = self.supabase.from_("base_conhecimento") \
                .select("*") \
                .limit(limit) \
                .execute()

            if hasattr(response, 'data'):
                results = response.data or []
            else:
                results = response or []
                
            logger.info("Documentos encontrados: %d", len(results))
            
            # Filtra localmente se encontrou documentos
            if results:
                filtered = []
                query_terms = set(query.lower().split())
                
                for doc in results:
                    content = doc.get('conteudo', {})
                    if isinstance(content, str):
                        try:
                            content = json.loads(content)
                        except:
                            content = {"text": content}
                            
                    text = content.get('text', '')
                    title = doc.get('titulo', '')
                    
                    # Busca por termos individuais
                    doc_text = f"{title} {text}".lower()
                    matches = sum(1 for term in query_terms if term in doc_text)
                    
                    # Se encontrou pelo menos um termo
                    if matches > 0:
                        doc['relevance'] = matches / len(query_terms)
                        filtered.append(doc)
                        
                # Ordena por relevância
                filtered.sort(key=lambda x: x.get('relevance', 0), reverse=True)
                        
                logger.info("Documentos filtrados: %d", len(filtered))
                return filtered[:limit]
                
            return []

        except Exception as e:
            logger.warning("Erro na busca textual: %s", e)
            return []
