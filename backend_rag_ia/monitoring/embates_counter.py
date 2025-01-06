from typing import Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GlobalEmbatesCounter:
    def __init__(self):
        self._total_calls = 0
        self._calls_by_embate: Dict[str, int] = {}
        self._last_call_time: Dict[str, datetime] = {}

    def increment(self, embate_id: str) -> None:
        """Incrementa contadores e registra timestamp"""
        self._total_calls += 1
        self._calls_by_embate[embate_id] = self._calls_by_embate.get(embate_id, 0) + 1
        self._last_call_time[embate_id] = datetime.now()

        # Log para monitoramento
        logger.info(
            f"Chamada registrada - Embate: {embate_id}, "
            f"Total: {self._total_calls}, "
            f"Embate Total: {self._calls_by_embate[embate_id]}"
        )

    def get_total_calls(self) -> int:
        """Retorna total de chamadas do sistema"""
        return self._total_calls

    def get_embate_calls(self, embate_id: str) -> int:
        """Retorna total de chamadas de um embate específico"""
        return self._calls_by_embate.get(embate_id, 0)

    def get_last_call_time(self, embate_id: str) -> datetime:
        """Retorna timestamp da última chamada do embate"""
        return self._last_call_time.get(embate_id)

    def get_statistics(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        return {
            "total_calls": self._total_calls,
            "unique_embates": len(self._calls_by_embate),
            "most_active_embate": max(
                self._calls_by_embate.items(), key=lambda x: x[1], default=(None, 0)
            ),
            "last_call": max(self._last_call_time.values(), default=None)
            if self._last_call_time
            else None,
        }
