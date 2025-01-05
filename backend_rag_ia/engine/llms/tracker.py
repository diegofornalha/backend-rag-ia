"""
Módulo para tracking de métricas do LLM.
"""

from typing import Dict, Any
from collections import defaultdict

class LlmTracker:
    """Rastreador de métricas do LLM."""
    
    def __init__(self):
        """Inicializa o rastreador."""
        self.metrics = defaultdict(int)
        self.events = []
        
    def track_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Registra um evento."""
        self.events.append({
            "type": event_type,
            "data": data
        })
        self.metrics[event_type] += 1
        
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna as métricas coletadas."""
        return {
            "events_count": len(self.events),
            "events_by_type": dict(self.metrics),
            "last_events": self.events[-5:] if self.events else []
        } 