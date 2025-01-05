"""
Sistema de tracking para LLMs.
"""

from typing import Dict, Any, List
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class LlmTracker:
    """Sistema de tracking para uso de LLMs."""
    
    def __init__(self):
        """Inicializa o tracker."""
        self.events: List[Dict[str, Any]] = []
        self.metrics = defaultdict(int)
        self.start_time = time.time()
    
    def track_event(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> None:
        """Registra um evento no sistema."""
        try:
            # Prepara evento
            event = {
                "type": event_type,
                "timestamp": time.time(),
                "data": data
            }
            
            # Registra evento
            self.events.append(event)
            
            # Atualiza métricas
            self.metrics["total_events"] += 1
            self.metrics[f"events_{event_type}"] += 1
            
            # Log do evento
            logger.info(f"Evento registrado: {event_type}")
            logger.debug(f"Dados do evento: {data}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar evento: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do sistema."""
        try:
            # Calcula métricas
            uptime = time.time() - self.start_time
            events_per_minute = (
                self.metrics["total_events"] / (uptime / 60)
                if uptime > 0 else 0
            )
            
            return {
                "total_events": self.metrics["total_events"],
                "uptime_seconds": round(uptime, 2),
                "events_per_minute": round(events_per_minute, 2),
                "event_types": dict(self.metrics)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {str(e)}")
            return {}
    
    def get_recent_events(
        self,
        limit: int = 10,
        event_type: str = None
    ) -> List[Dict[str, Any]]:
        """Retorna eventos recentes do sistema."""
        try:
            # Filtra eventos
            filtered = self.events
            if event_type:
                filtered = [
                    e for e in filtered
                    if e["type"] == event_type
                ]
            
            # Retorna mais recentes
            return sorted(
                filtered,
                key=lambda x: x["timestamp"],
                reverse=True
            )[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao recuperar eventos: {str(e)}")
            return []
    
    def clear_events(self) -> None:
        """Limpa eventos antigos."""
        try:
            self.events = []
            logger.info("Eventos limpos com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao limpar eventos: {str(e)}")
    
    def get_event_types(self) -> List[str]:
        """Retorna tipos de eventos registrados."""
        try:
            return list({
                e["type"] for e in self.events
            })
            
        except Exception as e:
            logger.error(f"Erro ao listar tipos de eventos: {str(e)}")
            return []
