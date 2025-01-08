from typing import Any, Callable, Dict, List, Optional
from datetime import datetime
import asyncio
import json
from enum import Enum

class EmbateEventType(Enum):
    """Tipos de eventos do sistema de embates"""
    STARTED = "embate_started"
    COMPLETED = "embate_completed"
    FAILED = "embate_failed"
    RATE_LIMITED = "embate_rate_limited"
    CACHE_HIT = "embate_cache_hit"
    CACHE_MISS = "embate_cache_miss"
    CONTEXT_UPDATED = "embate_context_updated"

class EmbateEvent:
    """Evento do sistema de embates"""
    
    def __init__(
        self,
        event_type: EmbateEventType,
        embate_id: str,
        data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.type = event_type
        self.embate_id = embate_id
        self.data = data or {}
        self.timestamp = timestamp or datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte evento para dicionário"""
        return {
            "type": self.type.value,
            "embate_id": self.embate_id,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

class EventManager:
    """Gerenciador de eventos para comunicação assíncrona"""
    
    def __init__(self):
        self._subscribers: Dict[EmbateEventType, List[Callable]] = {}
        self._event_queue: asyncio.Queue[EmbateEvent] = asyncio.Queue()
        self._processing = False
        self._lock = asyncio.Lock()
        
    async def subscribe(
        self,
        event_type: EmbateEventType,
        callback: Callable[[EmbateEvent], None]
    ) -> None:
        """Registra um callback para um tipo de evento"""
        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            
    async def unsubscribe(
        self,
        event_type: EmbateEventType,
        callback: Callable[[EmbateEvent], None]
    ) -> None:
        """Remove um callback registrado"""
        async with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type].remove(callback)
                
    async def publish(self, event: EmbateEvent) -> None:
        """Publica um evento para processamento"""
        await self._event_queue.put(event)
        
        if not self._processing:
            asyncio.create_task(self._process_events())
            
    async def _process_events(self) -> None:
        """Processa eventos da fila"""
        self._processing = True
        
        try:
            while True:
                event = await self._event_queue.get()
                
                # Notifica subscribers
                if event.type in self._subscribers:
                    for callback in self._subscribers[event.type]:
                        try:
                            await callback(event)
                        except Exception as e:
                            print(f"Erro no callback do evento {event.type}: {e}")
                            
                self._event_queue.task_done()
                
                # Para processamento se não há mais eventos
                if self._event_queue.empty():
                    break
                    
        finally:
            self._processing = False
            
class EmbateEventManager(EventManager):
    """Gerenciador específico para eventos de embates"""
    
    async def notify_started(self, embate_id: str, context: Dict[str, Any]) -> None:
        """Notifica início de um embate"""
        event = EmbateEvent(
            EmbateEventType.STARTED,
            embate_id,
            {"context": context}
        )
        await self.publish(event)
        
    async def notify_completed(
        self,
        embate_id: str,
        result: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> None:
        """Notifica conclusão de um embate"""
        event = EmbateEvent(
            EmbateEventType.COMPLETED,
            embate_id,
            {
                "result": result,
                "metrics": metrics
            }
        )
        await self.publish(event)
        
    async def notify_failed(
        self,
        embate_id: str,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Notifica falha em um embate"""
        event = EmbateEvent(
            EmbateEventType.FAILED,
            embate_id,
            {
                "error": str(error),
                "context": context
            }
        )
        await self.publish(event)
        
    async def notify_rate_limited(self, embate_id: str) -> None:
        """Notifica que um embate foi limitado por taxa"""
        event = EmbateEvent(
            EmbateEventType.RATE_LIMITED,
            embate_id
        )
        await self.publish(event)
        
    async def notify_cache_result(
        self,
        embate_id: str,
        hit: bool,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Notifica resultado de busca no cache"""
        event = EmbateEvent(
            EmbateEventType.CACHE_HIT if hit else EmbateEventType.CACHE_MISS,
            embate_id,
            {"context": context}
        )
        await self.publish(event) 