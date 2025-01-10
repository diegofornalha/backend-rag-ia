from typing import Dict, Any, Optional, TypeVar, Generic
from datetime import datetime, timedelta
import json
import asyncio
import logging
from enum import Enum
import aioredis
from aioredis.client import Redis

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheStrategy(Enum):
    """Estratégias de cache disponíveis"""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"    # Para implementação futura

class CachePolicy(Enum):
    """Políticas de expiração de cache"""
    LRU = "lru"      # Least Recently Used
    LFU = "lfu"      # Least Frequently Used
    FIFO = "fifo"    # First In First Out

class CacheEntry(Generic[T]):
    """Entrada de cache com metadados"""
    
    def __init__(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.key = key
        self.value = value
        self.created_at = datetime.utcnow()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl  # Tempo de vida em segundos
        self.metadata = metadata or {}
        
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        if self.ttl is None:
            return False
        return (datetime.utcnow() - self.created_at).total_seconds() > self.ttl
        
    def access(self):
        """Registra acesso à entrada"""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte entrada para dicionário"""
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "ttl": self.ttl,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry[T]':
        """Cria entrada a partir de dicionário"""
        entry = cls(
            key=data["key"],
            value=data["value"],
            ttl=data.get("ttl"),
            metadata=data.get("metadata", {})
        )
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.last_accessed = datetime.fromisoformat(data["last_accessed"])
        entry.access_count = data["access_count"]
        return entry

class CacheManager(Generic[T]):
    """Gerenciador de cache genérico"""
    
    def __init__(
        self,
        strategy: CacheStrategy = CacheStrategy.REDIS,  # Alterado para REDIS por padrão
        policy: CachePolicy = CachePolicy.LRU,
        max_size: int = 1000,
        default_ttl: Optional[int] = 3600,  # 1 hora
        redis_url: Optional[str] = None
    ):
        self.strategy = strategy
        self.policy = policy
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry[T]] = {}
        self._cleanup_task = None
        self._redis: Optional[Redis] = None
        self._redis_url = redis_url or "redis://localhost:6379"
        
    async def start(self):
        """Inicia o gerenciador de cache"""
        if self.strategy == CacheStrategy.REDIS:
            try:
                self._redis = await aioredis.from_url(
                    self._redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()
                logger.info("Conexão com Redis estabelecida")
            except Exception as e:
                logger.error(f"Erro ao conectar ao Redis: {e}")
                self.strategy = CacheStrategy.MEMORY
                logger.warning("Fallback para cache em memória")
                
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Cache iniciado com estratégia {self.strategy.value}")
        
    async def stop(self):
        """Para o gerenciador de cache"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        if self._redis:
            await self._redis.close()
            
        logger.info("Cache parado")
        
    async def get(self, key: str) -> Optional[T]:
        """Recupera valor do cache"""
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                data = await self._redis.get(f"cache:{key}")
                if not data:
                    return None
                    
                entry = CacheEntry.from_dict(json.loads(data))
                
                if entry.is_expired():
                    await self.delete(key)
                    return None
                    
                entry.access()
                await self._redis.set(
                    f"cache:{key}",
                    json.dumps(entry.to_dict()),
                    ex=entry.ttl
                )
                return entry.value
                
            except Exception as e:
                logger.error(f"Erro ao recuperar do Redis: {e}")
                return await self._get_from_memory(key)
        else:
            return await self._get_from_memory(key)
            
    async def _get_from_memory(self, key: str) -> Optional[T]:
        """Recupera valor do cache em memória"""
        entry = self._cache.get(key)
        
        if entry is None:
            return None
            
        if entry.is_expired():
            await self.delete(key)
            return None
            
        entry.access()
        return entry.value
        
    async def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Armazena valor no cache"""
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl or self.default_ttl,
            metadata=metadata
        )
        
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                await self._redis.set(
                    f"cache:{key}",
                    json.dumps(entry.to_dict()),
                    ex=entry.ttl
                )
                return
            except Exception as e:
                logger.error(f"Erro ao armazenar no Redis: {e}")
                await self._set_in_memory(key, entry)
        else:
            await self._set_in_memory(key, entry)
            
    async def _set_in_memory(self, key: str, entry: CacheEntry[T]):
        """Armazena valor no cache em memória"""
        if len(self._cache) >= self.max_size:
            await self._evict()
        self._cache[key] = entry
        
    async def delete(self, key: str):
        """Remove valor do cache"""
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                await self._redis.delete(f"cache:{key}")
            except Exception as e:
                logger.error(f"Erro ao remover do Redis: {e}")
                
        self._cache.pop(key, None)
        
    async def clear(self):
        """Limpa todo o cache"""
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                keys = await self._redis.keys("cache:*")
                if keys:
                    await self._redis.delete(*keys)
            except Exception as e:
                logger.error(f"Erro ao limpar Redis: {e}")
                
        self._cache.clear()
        
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        stats = {
            "strategy": self.strategy.value,
            "policy": self.policy.value,
            "max_size": self.max_size
        }
        
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                info = await self._redis.info()
                keys = await self._redis.keys("cache:*")
                
                stats.update({
                    "total_entries": len(keys),
                    "redis_used_memory": info.get("used_memory_human"),
                    "redis_hits": info.get("keyspace_hits"),
                    "redis_misses": info.get("keyspace_misses"),
                    "redis_connected_clients": info.get("connected_clients")
                })
            except Exception as e:
                logger.error(f"Erro ao obter estatísticas do Redis: {e}")
                stats.update(await self._get_memory_stats())
        else:
            stats.update(await self._get_memory_stats())
            
        return stats
        
    async def _get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache em memória"""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
        
        access_counts = [entry.access_count for entry in self._cache.values()]
        avg_access = sum(access_counts) / total_entries if total_entries > 0 else 0
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "avg_access_count": avg_access
        }
        
    async def _cleanup_loop(self):
        """Loop de limpeza de entradas expiradas"""
        while True:
            try:
                await asyncio.sleep(60)  # Executa a cada minuto
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro na limpeza do cache: {e}")
                
    async def _cleanup_expired(self):
        """Remove entradas expiradas"""
        if self.strategy == CacheStrategy.REDIS and self._redis:
            try:
                keys = await self._redis.keys("cache:*")
                for key in keys:
                    data = await self._redis.get(key)
                    if data:
                        entry = CacheEntry.from_dict(json.loads(data))
                        if entry.is_expired():
                            await self._redis.delete(key)
            except Exception as e:
                logger.error(f"Erro ao limpar entradas expiradas do Redis: {e}")
                
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            await self.delete(key)
            
        if expired_keys:
            logger.debug(f"Removidas {len(expired_keys)} entradas expiradas do cache")
            
    async def _evict(self):
        """Remove entradas conforme política de cache"""
        if not self._cache:
            return
            
        if self.policy == CachePolicy.LRU:
            # Remove entrada menos recentemente acessada
            key_to_remove = min(
                self._cache.items(),
                key=lambda x: x[1].last_accessed
            )[0]
        elif self.policy == CachePolicy.LFU:
            # Remove entrada menos frequentemente acessada
            key_to_remove = min(
                self._cache.items(),
                key=lambda x: x[1].access_count
            )[0]
        else:  # FIFO
            # Remove entrada mais antiga
            key_to_remove = min(
                self._cache.items(),
                key=lambda x: x[1].created_at
            )[0]
            
        await self.delete(key_to_remove)
        logger.debug(f"Entrada {key_to_remove} removida por política {self.policy.value}")

class EmbateCache:
    """Cache específico para embates"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.cache = CacheManager[Dict[str, Any]](
            strategy=CacheStrategy.REDIS,
            policy=CachePolicy.LRU,
            max_size=1000,
            default_ttl=3600,
            redis_url=redis_url
        )
        
    async def start(self):
        """Inicia o cache de embates"""
        await self.cache.start()
        
    async def stop(self):
        """Para o cache de embates"""
        await self.cache.stop()
        
    async def get_result(
        self,
        context_hash: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Recupera resultado de embate do cache"""
        result = await self.cache.get(context_hash)
        
        if result:
            logger.info(
                "Cache hit",
                extra={"context_hash": context_hash, "metadata": metadata}
            )
        else:
            logger.debug(
                "Cache miss",
                extra={"context_hash": context_hash, "metadata": metadata}
            )
            
        return result
        
    async def store_result(
        self,
        context_hash: str,
        result: Dict[str, Any],
        ttl: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Armazena resultado de embate no cache"""
        await self.cache.set(
            key=context_hash,
            value=result,
            ttl=ttl,
            metadata=metadata
        )
        
        logger.info(
            "Resultado armazenado em cache",
            extra={
                "context_hash": context_hash,
                "ttl": ttl,
                "metadata": metadata
            }
        )
        
    async def invalidate_result(self, context_hash: str):
        """Invalida resultado de embate no cache"""
        await self.cache.delete(context_hash)
        
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache de embates"""
        return await self.cache.get_stats() 