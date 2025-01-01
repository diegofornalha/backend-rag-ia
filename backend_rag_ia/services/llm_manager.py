"""Gerenciador de LLM."""

import os
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
import google.generativeai as genai
from google.api_core import exceptions
import json

from backend_rag_ia.constants import (
    DEFAULT_SEARCH_LIMIT,
    ERROR_GOOGLE_API_KEY,
)
from backend_rag_ia.exceptions import LLMError
from backend_rag_ia.utils.logging_config import logger

class LLMManager:
    """Gerenciador de LLM."""

    def __init__(self) -> None:
        """Inicializa o gerenciador."""
        self.model = self._init_llm()
        self.max_retries = 3
        self.base_delay = 1  # segundos
        self._cache: Dict[str, Any] = {}  # Cache simples em memória
        self._cache_hits = 0
        self._cache_misses = 0

    def _init_llm(self) -> Any:
        """Inicializa o modelo LLM."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY não configurada")
            raise LLMError("GEMINI_API_KEY deve ser configurada")

        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.exception("Erro ao inicializar LLM: %s", e)
            raise LLMError from e

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Busca resposta no cache."""
        if key in self._cache:
            self._cache_hits += 1
            logger.info(f"Cache hit ({self._cache_hits} hits / {self._cache_misses} misses)")
            return self._cache[key]
        self._cache_misses += 1
        return None

    def _save_to_cache(self, key: str, value: Any) -> None:
        """Salva resposta no cache."""
        self._cache[key] = value
        logger.debug(f"Resposta salva no cache (key={key[:8]}...)")

    def _generate_with_retry(self, prompt: str) -> Any:
        """Gera conteúdo com retry em caso de erro."""
        # Verifica cache
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    safety_settings=[
                        {
                            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                            "threshold": "BLOCK_NONE",
                        }
                    ],
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )
                
                # Verifica se a resposta foi bloqueada
                if not response.text:
                    if attempt == self.max_retries - 1:
                        return self._fallback_response("Resposta bloqueada pelo modelo")
                    continue
                    
                # Salva no cache
                self._save_to_cache(cache_key, response)
                return response
                
            except exceptions.ResourceExhausted:
                if attempt == self.max_retries - 1:
                    return self._fallback_response("Quota da API excedida")
                delay = self.base_delay * (2 ** attempt)  # Backoff exponencial
                logger.warning(f"Quota excedida, tentando novamente em {delay}s...")
                time.sleep(delay)
            except exceptions.InvalidArgument as e:
                logger.error(f"Erro nos argumentos da API: {e}")
                return self._fallback_response("Erro nos argumentos da API")
            except exceptions.FailedPrecondition as e:
                logger.error(f"API não inicializada corretamente: {e}")
                return self._fallback_response("API não inicializada corretamente")
            except Exception as e:
                logger.exception("Erro ao gerar conteúdo: %s", e)
                return self._fallback_response(f"Erro inesperado: {str(e)}")

    def _fallback_response(self, reason: str = "") -> Any:
        """Retorna uma resposta simples quando a API não está disponível."""
        class FallbackResponse:
            def __init__(self, text):
                self.text = text
                
        error_msg = "Não foi possível processar a requisição no momento"
        if reason:
            error_msg += f" ({reason})"
        error_msg += ". Por favor, tente novamente mais tarde."
        
        return FallbackResponse(error_msg)

    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = DEFAULT_SEARCH_LIMIT,
    ) -> List[Dict[str, Any]]:
        """Reordena resultados por relevância."""
        if not results:
            return []
            
        try:
            # Tenta usar LLM
            prompt = f"""Query: {query}

Documentos:
{self._format_documents(results)}

Liste os {top_k} IDs mais relevantes para a query, separados por vírgula:"""
            
            response = self._generate_with_retry(prompt)
            
            if "API indisponível" in response.text:
                # Fallback: busca por palavras-chave
                return self._keyword_search(query, results, top_k)
            
            # Processa resposta do LLM
            relevant_ids = [id.strip() for id in response.text.split(",")]
            
            # Filtra e ordena resultados
            id_to_doc = {str(doc["id"]): doc for doc in results}
            reranked = []
            for id in relevant_ids:
                if id in id_to_doc:
                    reranked.append(id_to_doc[id])
                    
            return reranked

        except Exception as e:
            logger.exception("Erro ao reordenar resultados: %s", e)
            return self._keyword_search(query, results, top_k)

    def process_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Processa resultados com LLM."""
        if not results:
            return {
                "answer": "Nenhum documento relevante encontrado",
                "results": []
            }
            
        try:
            # Tenta usar LLM
            prompt = f"""Query: {query}

Documentos:
{self._format_documents(results)}

Responda à query com base nos documentos fornecidos:"""
            
            response = self._generate_with_retry(prompt)
            
            if "API indisponível" in response.text:
                # Fallback: resposta simples
                return {
                    "answer": "Não foi possível processar a resposta com IA. Aqui estão os documentos mais relevantes encontrados:",
                    "results": results
                }
            
            return {
                "answer": response.text,
                "results": results
            }

        except Exception as e:
            logger.exception("Erro ao processar resultados: %s", e)
            return {
                "answer": f"Erro ao processar resultados: {str(e)}",
                "results": results
            }
            
    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Formata documentos para prompt."""
        formatted = []
        for doc in documents:
            # Extrai título ou usa um padrão
            title = self._sanitize_text(doc.get('titulo', 'Documento'))
            
            # Extrai conteúdo do documento
            content = doc.get('conteudo', {})
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    content = {"text": content}
                    
            text = content.get('text', '')
            text = self._sanitize_text(text)
            
            # Formata documento
            formatted.append(f"ID: {doc.get('id', '')}\nTítulo: {title}\nConteúdo: {text}\n")
            
        return "\n".join(formatted)
        
    def _sanitize_text(self, text: str) -> str:
        """Sanitiza texto para envio ao Gemini."""
        # Remove caracteres não-ASCII
        text = text.encode('ascii', 'ignore').decode()
        # Remove caracteres de controle
        text = "".join(ch for ch in text if ord(ch) >= 32)
        # Remove múltiplos espaços
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    def _keyword_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Realiza busca por palavras-chave."""
        # Extrai palavras-chave da query
        keywords = set(query.lower().split())
        
        # Calcula score para cada documento
        scored_docs = []
        for doc in documents:
            # Extrai texto do documento
            content = doc.get('conteudo', {})
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    content = {"text": content}
                    
            text = content.get('text', '')
            title = doc.get('titulo', 'Documento')
            text = f"{title} {text}"
            
            # Calcula score
            text_words = set(text.lower().split())
            score = len(keywords.intersection(text_words))
            scored_docs.append((score, doc))
            
        # Ordena por score e retorna top_k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for score, doc in scored_docs[:top_k]] 