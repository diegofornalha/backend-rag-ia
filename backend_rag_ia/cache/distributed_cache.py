from typing import Any, Dict, Optional, List
import json
import logging
import redis
from datetime import datetime, timedelta
from ..config.redis_config import RedisConfig
from ..monitoring.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class DistributedCache:
    """Cache distribuído usando Redis"""

    def __init__(self):
        """Inicializa o cache distribuído"""
        self.redis_url = RedisConfig.get_redis_url()
        self.ttl = RedisConfig.get_ttl()
        self.redis = redis.from_url(self.redis_url)
        self.metrics = MetricsCollector()

        # Testa conexão
        try:
            self.redis.ping()
            logger.info("Conexão com Redis estabelecida com sucesso")
        except redis.ConnectionError as e:
            logger.error(f"Erro ao conectar ao Redis: {str(e)}")
            raise

    def _serialize(self, value: Any) -> str:
        """
        Serializa valor para armazenamento

        Args:
            value: Valor a ser serializado

        Returns:
            String JSON
        """
        try:
            return json.dumps(value)
        except Exception as e:
            logger.error(f"Erro ao serializar valor: {str(e)}")
            raise

    def _deserialize(self, value: str) -> Any:
        """
        Deserializa valor do cache

        Args:
            value: String JSON

        Returns:
            Valor deserializado
        """
        try:
            return json.loads(value)
        except Exception as e:
            logger.error(f"Erro ao deserializar valor: {str(e)}")
            raise

    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache

        Args:
            key: Chave do valor

        Returns:
            Valor armazenado ou None se não encontrado
        """
        try:
            value = self.redis.get(key)
            if value:
                self.metrics.registrar_cache_hit()
                return self._deserialize(value)

            self.metrics.registrar_cache_miss()
            return None

        except Exception as e:
            logger.error(f"Erro ao obter valor do cache: {str(e)}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Armazena valor no cache

        Args:
            key: Chave do valor
            value: Valor a ser armazenado
            ttl: TTL em segundos (opcional)

        Returns:
            True se armazenado com sucesso, False caso contrário
        """
        try:
            serialized = self._serialize(value)
            self.redis.set(key, serialized, ex=ttl or self.ttl)
            self.metrics.atualizar_tamanho_cache(len(self.redis.keys("*")))
            return True

        except Exception as e:
            logger.error(f"Erro ao armazenar valor no cache: {str(e)}")
            return False

    def delete(self, key: str) -> bool:
        """
        Remove valor do cache

        Args:
            key: Chave do valor

        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            result = self.redis.delete(key)
            self.metrics.atualizar_tamanho_cache(len(self.redis.keys("*")))
            return result > 0

        except Exception as e:
            logger.error(f"Erro ao remover valor do cache: {str(e)}")
            return False

    def clear(self) -> bool:
        """
        Limpa todo o cache

        Returns:
            True se limpo com sucesso, False caso contrário
        """
        try:
            self.redis.flushdb()
            self.metrics.registrar_limpeza_cache()
            return True

        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            return False

    def get_stats(self) -> Dict:
        """
        Obtém estatísticas do cache

        Returns:
            Dicionário com estatísticas
        """
        try:
            info = self.redis.info()
            keys = len(self.redis.keys("*"))

            return {
                "total_keys": keys,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "uptime_days": info.get("uptime_in_days", 0),
                "hit_rate": self.metrics.cache_metrics.hit_rate,
                "last_cleanup": self.metrics.cache_metrics.ultima_limpeza,
            }

        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {str(e)}")
            return {}
