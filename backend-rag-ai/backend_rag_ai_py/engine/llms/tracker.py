"""
Módulo para tracking de métricas do LLM.
"""

from collections import defaultdict
from typing import Any, Dict


class LlmTracker:
    """Rastreador de métricas do LLM."""

    def __init__(self):
        """Inicializa o rastreador."""
        self.metrics = defaultdict(int)
        self.events = []

    def track_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Registra um evento."""
        self.events.append({"type": event_type, "data": data})
        self.metrics[event_type] += 1

    def get_metrics(self) -> dict[str, Any]:
        """Retorna as métricas coletadas."""
        return {
            "events_count": len(self.events),
            "events_by_type": dict(self.metrics),
            "last_events": self.events[-5:] if self.events else [],
        }
