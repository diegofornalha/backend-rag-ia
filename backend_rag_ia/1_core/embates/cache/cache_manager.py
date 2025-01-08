from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import asyncio
import json
import os

class CacheManager:
    """Gerenciador de cache para otimização de embates"""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """Recupera um valor do cache"""
        async with self._lock:
            if key not in self._cache:
                return None
                
            cache_data = self._cache[key]
            if self._is_expired(cache_data["timestamp"]):
                del self._cache[key]
                return None
                
            return cache_data["value"]
            
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena um valor no cache"""
        async with self._lock:
            self._cache[key] = {
                "value": value,
                "timestamp": datetime.utcnow(),
                "ttl": ttl or self._ttl
            }
            
    async def delete(self, key: str) -> None:
        """Remove um valor do cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self) -> None:
        """Limpa todo o cache"""
        async with self._lock:
            self._cache.clear()
            
    def _is_expired(self, timestamp: datetime) -> bool:
        """Verifica se um item do cache expirou"""
        return datetime.utcnow() - timestamp > timedelta(seconds=self._ttl)
        
    async def cleanup(self) -> None:
        """Remove itens expirados do cache"""
        async with self._lock:
            expired_keys = [
                key for key, data in self._cache.items()
                if self._is_expired(data["timestamp"])
            ]
            for key in expired_keys:
                del self._cache[key]
                
class EmbateCache(CacheManager):
    """Cache específico para resultados de embates"""
    
    def __init__(self, ttl_seconds: int = 300):
        super().__init__(ttl_seconds)
        self._result_cache = CacheManager(ttl_seconds)
        self._context_cache = CacheManager(ttl_seconds * 2)  # Contexto tem TTL maior
        
    async def get_result(self, embate_id: str) -> Optional[Dict[str, Any]]:
        """Recupera resultado de um embate do cache"""
        return await self._result_cache.get(embate_id)
        
    async def set_result(self, embate_id: str, result: Dict[str, Any]) -> None:
        """Armazena resultado de um embate no cache"""
        await self._result_cache.set(embate_id, result)
        
    async def get_context(self, embate_id: str) -> Optional[Dict[str, Any]]:
        """Recupera contexto de um embate do cache"""
        return await self._context_cache.get(embate_id)
        
    async def set_context(self, embate_id: str, context: Dict[str, Any]) -> None:
        """Armazena contexto de um embate no cache"""
        await self._context_cache.set(embate_id, context)
        
    async def invalidate_embate(self, embate_id: str) -> None:
        """Invalida cache de um embate específico"""
        await self._result_cache.delete(embate_id)
        await self._context_cache.delete(embate_id)
        
    async def cleanup_all(self) -> None:
        """Limpa caches expirados"""
        await self._result_cache.cleanup()
        await self._context_cache.cleanup() 