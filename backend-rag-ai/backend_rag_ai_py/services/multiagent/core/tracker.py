"""
Sistema de tracking para o multiagente.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config import get_multiagent_config
from .logging import get_multiagent_logger

logger = get_multiagent_logger(__name__)


class EventTracker:
    """Rastreador de eventos do sistema multiagente."""

    def __init__(self):
        """Inicializa o tracker."""
        self.events: list[dict[str, Any]] = []
        self.config = get_multiagent_config()
        self.start_time = time.time()

    def track_event(self, event_type: str, data: dict[str, Any] | None = None) -> None:
        """
        Registra um evento no sistema.

        Args:
            event_type: Tipo do evento (ex: 'task_start', 'error')
            data: Dados adicionais do evento
        """
        if not self.config.tracking_enabled:
            return

        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
            "elapsed_time": time.time() - self.start_time,
        }

        self.events.append(event)
        logger.debug(f"Evento registrado: {event_type}")

    def get_metrics(self) -> dict[str, Any]:
        """Retorna métricas do sistema."""
        if not self.events:
            return {"total_events": 0, "elapsed_time": 0, "events_by_type": {}}

        events_by_type = {}
        for event in self.events:
            event_type = event["type"]
            events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

        return {
            "total_events": len(self.events),
            "elapsed_time": time.time() - self.start_time,
            "events_by_type": events_by_type,
            "last_event": self.events[-1] if self.events else None,
        }

    def clear(self) -> None:
        """Limpa todos os eventos registrados."""
        self.events.clear()
        self.start_time = time.time()
        logger.debug("Eventos limpos")
