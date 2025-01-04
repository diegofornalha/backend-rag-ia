from typing import Dict, Optional
import hashlib
import json
from datetime import datetime, timedelta
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class EmbatesCache:
    def __init__(self, cache_ttl_minutes: int = 30):
        self._cache: Dict[str, Dict] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._ttl = timedelta(minutes=cache_ttl_minutes)
        
    def _generate_hash(self, embate_data: Dict) -> str:
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
        
    @lru_cache(maxsize=100)
    def get_validation_result(self, embate_data: Dict) -> Optional[Dict]:
        """Recupera resultado de validação do cache"""
        hash_key = self._generate_hash(embate_data)
        
        if hash_key in self._cache and self._is_valid(hash_key):
            logger.info(f"Cache hit para embate hash: {hash_key}")
            return self._cache[hash_key]
            
        logger.info(f"Cache miss para embate hash: {hash_key}")
        return None
        
    def store_validation(self, embate_data: Dict, result: Dict) -> None:
        """Armazena resultado de validação no cache"""
        hash_key = self._generate_hash(embate_data)
        self._cache[hash_key] = result
        self._timestamps[hash_key] = datetime.now()
        logger.info(f"Resultado armazenado em cache para hash: {hash_key}")
        
    def invalidate(self, embate_data: Dict) -> None:
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
        logger.info("Cache completamente limpo")
        
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do cache"""
        total = len(self._cache)
        valid = sum(1 for k in self._cache.keys() if self._is_valid(k))
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'invalid_entries': total - valid,
            'hit_ratio': self.get_validation_result.cache_info().hits / 
                        (self.get_validation_result.cache_info().hits + 
                         self.get_validation_result.cache_info().misses)
                        if self.get_validation_result.cache_info().hits > 0 else 0
        } 