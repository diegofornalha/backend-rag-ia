from dataclasses import dataclass
from typing import Dict


@dataclass
class EmbatesConfig:
    # Limites
    MAX_TOOLS_PER_EMBATE: int = 3
    WARNING_THRESHOLD: int = 2

    # Cache
    CACHE_TTL_MINUTES: int = 30
    MAX_CACHE_ENTRIES: int = 100

    # Métricas
    MAX_HISTORY: int = 1000
    METRICS_ROTATION_SIZE: int = 10000

    # Proteção
    RATE_LIMIT_WINDOW: int = 60  # segundos
    MAX_CALLS_PER_WINDOW: int = 100

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def get_default(cls) -> "EmbatesConfig":
        return cls()

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "EmbatesConfig":
        """Cria configuração a partir de um dicionário"""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})

    def to_dict(self) -> Dict:
        """Converte configuração para dicionário"""
        return {k: getattr(self, k) for k in self.__annotations__}
