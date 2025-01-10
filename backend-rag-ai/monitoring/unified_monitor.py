import logging
from datetime import datetime
from typing import Dict, Optional

from ..config.embates_config import EmbatesConfig
from .embates_cache import EmbatesCache
from .embates_counter import GlobalEmbatesCounter
from .embates_metrics import EmbateMetric, EmbatesMetrics

logger = logging.getLogger(__name__)


class UnifiedMonitor:
    def __init__(self, config: EmbatesConfig | None = None):
        self.config = config or EmbatesConfig.get_default()

        # Configuração de logging
        logging.basicConfig(level=self.config.LOG_LEVEL, format=self.config.LOG_FORMAT)

        # Inicialização dos componentes
        self.metrics = EmbatesMetrics(max_history=self.config.MAX_HISTORY)
        self.cache = EmbatesCache(cache_ttl_minutes=self.config.CACHE_TTL_MINUTES)
        self.counter = GlobalEmbatesCounter()

    def record_operation(
        self,
        embate_id: str,
        operation: str,
        duration_ms: float,
        success: bool,
        error_type: str | None = None,
        details: dict | None = None,
    ) -> None:
        """Registra uma operação no sistema"""
        # Incrementa contador
        self.counter.increment(embate_id)

        # Registra métrica
        metric = EmbateMetric(
            timestamp=datetime.now(),
            embate_id=embate_id,
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            error_type=error_type,
            details=details,
        )
        self.metrics.record_operation(metric)

    def check_cache(self, embate_data: dict) -> dict | None:
        """Verifica cache para um embate"""
        return self.cache.get_validation_result(embate_data)

    def store_in_cache(self, embate_data: dict, result: dict) -> None:
        """Armazena resultado no cache"""
        self.cache.store_validation(embate_data, result)

    def get_statistics(self) -> dict:
        """Retorna estatísticas completas do sistema"""
        return {
            "counter": self.counter.get_statistics(),
            "cache": self.cache.get_statistics(),
            "metrics": self.metrics.get_statistics(),
        }

    def check_rate_limit(self, embate_id: str) -> bool:
        """Verifica limite de taxa para um embate"""
        window_start = datetime.now().timestamp() - self.config.RATE_LIMIT_WINDOW
        recent_calls = sum(
            1
            for m in self.metrics.get_metrics_by_embate(embate_id)
            if m.timestamp.timestamp() > window_start
        )
        return recent_calls < self.config.MAX_CALLS_PER_WINDOW

    def should_warn(self, embate_id: str) -> bool:
        """Verifica se deve emitir aviso para um embate"""
        calls = self.counter.get_embate_calls(embate_id)
        return calls == self.config.WARNING_THRESHOLD
