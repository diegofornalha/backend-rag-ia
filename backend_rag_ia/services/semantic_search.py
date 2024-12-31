from typing import Optional, List, Dict, Any
import os
import logging
from datetime import datetime
import httpx
import asyncio

logger = logging.getLogger(__name__)

class SemanticSearchManager:
    """Gerenciador de busca semântica com suporte a múltiplos modos."""

    def __init__(self):
        self.mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
        self.last_error = None
        self.last_success = None
        # URLs de teste - você deve substituir pelos endpoints reais
        self.local_url = "http://localhost:8000/search"
        self.render_url = "https://api.coflow.com.br/search"

    async def search(self, query: str, **kwargs) -> List[Dict[Any, Any]]:
        """
        Realiza busca semântica usando o modo configurado.
        No modo auto, tenta local primeiro e faz fallback para Render se necessário.
        """
        if self.mode == "auto":
            try:
                # Tenta busca local primeiro
                results = await self._search_local(query, **kwargs)
                self._update_status(success=True, mode="local")
                return results
            except Exception as e:
                logger.warning(f"Busca local falhou: {str(e)}. Tentando Render...")
                self._update_status(success=False, mode="local", error=str(e))
                
                try:
                    # Fallback para Render
                    results = await self._search_render(query, **kwargs)
                    self._update_status(success=True, mode="render")
                    return results
                except Exception as e2:
                    self._update_status(success=False, mode="render", error=str(e2))
                    raise Exception(f"Ambas as buscas falharam. Local: {str(e)}. Render: {str(e2)}")
        
        elif self.mode == "local":
            return await self._search_local(query, **kwargs)
        
        elif self.mode == "render":
            return await self._search_render(query, **kwargs)
        
        else:
            raise ValueError(f"Modo inválido: {self.mode}")

    async def _search_local(self, query: str, **kwargs) -> List[Dict[Any, Any]]:
        """Realiza busca usando pgvector local."""
        try:
            # Simula um pequeno delay para teste
            await asyncio.sleep(0.5)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.local_url,
                    json={"query": query, **kwargs},
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erro na busca local: {str(e)}")
            raise

    async def _search_render(self, query: str, **kwargs) -> List[Dict[Any, Any]]:
        """Realiza busca usando Supabase+pgvector no Render."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.render_url,
                    json={"query": query, **kwargs},
                    headers={"Authorization": f"Bearer {os.getenv('RENDER_API_KEY')}"},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Erro na busca no Render: {str(e)}")
            raise

    def _update_status(self, success: bool, mode: str, error: Optional[str] = None):
        """Atualiza o status da última operação."""
        timestamp = datetime.now()
        
        if success:
            self.last_success = {
                "timestamp": timestamp,
                "mode": mode
            }
            self.last_error = None
        else:
            self.last_error = {
                "timestamp": timestamp,
                "mode": mode,
                "error": error
            }

    def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do gerenciador."""
        return {
            "current_mode": self.mode,
            "last_success": self.last_success,
            "last_error": self.last_error,
            "available_modes": ["local", "render", "auto"],
            "is_healthy": self.last_error is None or (
                self.last_success and 
                self.last_success["timestamp"] > self.last_error["timestamp"]
            )
        } 