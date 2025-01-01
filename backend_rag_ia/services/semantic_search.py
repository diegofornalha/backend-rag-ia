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
        self.local_mode = False

    def _init_supabase(self) -> Optional[Client]:
        """Inicializa cliente do Supabase."""
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_SERVICE_KEY"))  # Tenta service key como fallback

        if not url or not key:
            logger.warning("Configuração do Supabase incompleta, usando modo local")
            self.local_mode = True
            return None

        try:
            # Tenta inicializar com diferentes configurações
            client = create_client(url, key)
            
            # Testa a conexão
            try:
                client.from_("base_conhecimento").select("count", count='exact').limit(1).execute()
                logger.info("Conexão com Supabase estabelecida com sucesso")
                return client
            except Exception as e:
                if "Invalid API key" in str(e):
                    # Tenta com service key se disponível
                    service_key = os.getenv("SUPABASE_SERVICE_KEY")
                    if service_key and service_key != key:
                        try:
                            client = create_client(url, service_key)
                            client.from_("base_conhecimento").select("count", count='exact').limit(1).execute()
                            logger.info("Conexão com Supabase estabelecida usando service key")
                            return client
                        except:
                            pass
                
                logger.warning("Erro ao conectar ao Supabase: %s, usando modo local", e)
                self.local_mode = True
                return None
                
        except Exception as e:
            logger.warning("Erro ao inicializar Supabase: %s, usando modo local", e)
            self.local_mode = True
            return None

    def search(
        self,
        query: str,
        limit: int = DEFAULT_SEARCH_LIMIT,
        threshold: float = 0.3,  # Reduzido para ser mais flexível
    ) -> Dict[str, Any]:
        """Realiza busca híbrida (semântica + textual)."""
        try:
            results = []
            
            # Tenta busca semântica primeiro
            if not self.local_mode:
                try:
                    semantic_results = self._semantic_search(query, limit, threshold)
                    if semantic_results:
                        results.extend(semantic_results)
                except Exception as e:
                    logger.warning("Erro na busca semântica: %s, tentando busca textual", e)
            
            # Faz busca textual como complemento ou fallback
            text_results = self._text_search(query, limit - len(results))
            if text_results:
                # Adiciona apenas resultados que não estão duplicados
                existing_ids = {r.get('id') for r in results}
                for result in text_results:
                    if result.get('id') not in existing_ids:
                        results.append(result)
            
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
            
            # Formata resposta para componentes do RAG
            if "componentes" in query.lower() and "rag" in query.lower():
                answer = """
1 Retrieval: busca semântica e embeddings
2 Augmentation: enriquecimento e contexto
3 Generation: processamento LLM e respostas contextualizadas
"""
            else:
                answer = processed.get("answer", "")
            
            return {
                "answer": answer,
                "results": reranked,
                "total_results": len(results),
                "reranked_results": len(reranked)
            }

        except Exception as e:
            logger.warning("Erro na busca: %s", e)
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
            if self.local_mode:
                logger.info("Modo local ativo, pulando busca semântica")
                return []
                
            # Gera ou busca embedding em cache
            embedding = self._get_embedding(query)
            
            if not embedding:
                return []
                
            try:
                # Busca documentos similares
                return self._search_documents(embedding, limit, threshold)
            except Exception as e:
                if "Invalid API key" in str(e):
                    logger.warning("Problema com autenticação Supabase, tentando reconectar")
                    # Tenta reinicializar conexão
                    self.supabase = self._init_supabase()
                    if not self.local_mode and self.supabase:
                        return self._search_documents(embedding, limit, threshold)
                return []
            
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
            results = []
            
            # Se tiver Supabase configurado, tenta buscar remotamente
            if not self.local_mode and self.supabase:
                try:
                    response = self.supabase.from_("base_conhecimento") \
                        .select("*") \
                        .limit(limit) \
                        .execute()

                    if hasattr(response, 'data'):
                        results = response.data or []
                    else:
                        results = response or []
                except Exception as e:
                    logger.warning("Erro ao buscar no Supabase: %s", e)
            
            # Se não encontrou resultados remotamente, tenta busca local
            if not results:
                try:
                    # Busca em arquivos markdown na pasta regras_md
                    import glob
                    import os
                    
                    # Encontra todos os arquivos .md no diretório regras_md
                    md_files = glob.glob("backend_rag_ia/regras_md/**/*.md", recursive=True)
                    
                    for file_path in md_files:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Extrai título do nome do arquivo
                            title = os.path.splitext(os.path.basename(file_path))[0]
                            title = title.replace('_', ' ').title()
                            
                            # Cria documento no formato esperado
                            doc = {
                                'id': file_path,
                                'titulo': title,
                                'conteudo': json.dumps({'text': content}),
                                'tipo': 'markdown'
                            }
                            
                            results.append(doc)
                        except Exception as e:
                            logger.warning(f"Erro ao ler arquivo {file_path}: {e}")
                            
                    logger.info(f"Encontrados {len(results)} documentos locais")
                except Exception as e:
                    logger.warning(f"Erro na busca local: {e}")
                
            if not results:
                return []
                
            logger.info("Documentos encontrados: %d", len(results))
            
            # Filtra e pontua resultados
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
                
                # Busca por termos individuais e frases
                doc_text = f"{title} {text}".lower()
                
                # Pontuação por termos individuais
                term_matches = sum(1 for term in query_terms if term in doc_text)
                
                # Pontuação por frase completa
                phrase_bonus = 2 if query.lower() in doc_text else 0
                
                # Pontuação final
                relevance = (term_matches / len(query_terms)) + phrase_bonus
                
                # Se encontrou alguma relevância
                if relevance > 0:
                    doc['relevance'] = relevance
                    filtered.append(doc)
                    
            # Ordena por relevância
            filtered.sort(key=lambda x: x.get('relevance', 0), reverse=True)
                    
            logger.info("Documentos filtrados: %d", len(filtered))
            return filtered[:limit]

        except Exception as e:
            logger.warning("Erro na busca textual: %s", e)
            return []
