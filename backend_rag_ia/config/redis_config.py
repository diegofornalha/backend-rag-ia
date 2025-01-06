import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class RedisConfig:
    """Configurações do Redis para cache distribuído"""

    # Configurações padrão
    DEFAULT_HOST = "localhost"
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0
    DEFAULT_TTL = 3600  # 1 hora

    @staticmethod
    def get_redis_url() -> str:
        """
        Obtém URL de conexão do Redis

        Returns:
            String com URL de conexão
        """
        host = os.getenv("REDIS_HOST", RedisConfig.DEFAULT_HOST)
        port = int(os.getenv("REDIS_PORT", RedisConfig.DEFAULT_PORT))
        db = int(os.getenv("REDIS_DB", RedisConfig.DEFAULT_DB))
        password = os.getenv("REDIS_PASSWORD")

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    @staticmethod
    def get_ttl() -> int:
        """
        Obtém TTL padrão para chaves

        Returns:
            TTL em segundos
        """
        return int(os.getenv("REDIS_TTL", RedisConfig.DEFAULT_TTL))
