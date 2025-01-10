import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class EmbatesCache:
    def __init__(self, cache_ttl_minutes: int = 30):
        self._cache: dict[str, dict] = {}
        self._timestamps: dict[str, datetime] = {}
        self._ttl = timedelta(minutes=cache_ttl_minutes)
        self._hits = 0
        self._misses = 0

    def _generate_hash(self, embate_data: dict) -> str:
        """Gera hash único para o embate"""
        # Ordena as chaves para garantir consistência
        serialized = json.dumps(embate_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    def _is_valid(self, hash_key: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if hash_key not in self._timestamps:
            return False

        age = datetime.now() - self._timestamps[hash_key]
        return age <= self._ttl

    def get_validation_result(self, embate_data: dict) -> dict | None:
        """Recupera resultado de validação do cache"""
        hash_key = self._generate_hash(embate_data)

        if hash_key in self._cache and self._is_valid(hash_key):
            logger.info(f"Cache hit para embate hash: {hash_key}")
            self._hits += 1
            return self._cache[hash_key]

        logger.info(f"Cache miss para embate hash: {hash_key}")
        self._misses += 1
        return None

    def store_validation(self, embate_data: dict, result: dict) -> None:
        """Armazena resultado de validação no cache"""
        hash_key = self._generate_hash(embate_data)
        self._cache[hash_key] = result
        self._timestamps[hash_key] = datetime.now()
        logger.info(f"Resultado armazenado em cache para hash: {hash_key}")

    def invalidate(self, embate_data: dict) -> None:
        """Invalida cache para um embate específico"""
        hash_key = self._generate_hash(embate_data)
        if hash_key in self._cache:
            del self._cache[hash_key]
            del self._timestamps[hash_key]
            logger.info(f"Cache invalidado para hash: {hash_key}")

    def clear(self) -> None:
        """Limpa todo o cache"""
        self._cache.clear()
        self._timestamps.clear()
        self._hits = 0
        self._misses = 0
        logger.info("Cache completamente limpo")

    def get_statistics(self) -> dict:
        """Retorna estatísticas do cache"""
        total = len(self._cache)
        valid = sum(1 for k in self._cache.keys() if self._is_valid(k))

        return {
            "total_entries": total,
            "valid_entries": valid,
            "invalid_entries": total - valid,
            "hit_ratio": self._hits / (self._hits + self._misses) if self._hits > 0 else 0,
        }
