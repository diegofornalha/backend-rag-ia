from typing import Dict, Any, Optional, List, Callable, Awaitable
from datetime import datetime
import asyncio
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Tipos de eventos do sistema de embates"""
    EMBATE_STARTED = "embate_started"
    EMBATE_COMPLETED = "embate_completed"
    EMBATE_FAILED = "embate_failed"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    STRATEGY_CHANGED = "strategy_changed"
    SYSTEM_ERROR = "system_error"

EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]

class EventManager:
    """Gerenciador de eventos para comunicação assíncrona"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[EventHandler]] = {
            event_type: [] for event_type in EventType
        }
        self._event_history: List[Dict[str, Any]] = []
        self._max_history = 1000
        self._lock = asyncio.Lock()
        
    async def subscribe(self, event_type: EventType, handler: EventHandler):
        """Registra um handler para um tipo de evento"""
        async with self._lock:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Handler registrado para evento {event_type.value}")
            
    async def unsubscribe(self, event_type: EventType, handler: EventHandler):
        """Remove um handler de um tipo de evento"""
        async with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Handler removido do evento {event_type.value}")
                
    async def publish(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Publica um evento para todos os subscribers"""
        event = {
            "type": event_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "metadata": metadata or {}
        }
        
        # Registra evento no histórico
        async with self._lock:
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
                
        # Notifica subscribers
        handlers = self._subscribers[event_type]
        if handlers:
            tasks = [
                asyncio.create_task(self._notify_handler(handler, event))
                for handler in handlers
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
            
        logger.debug(
            f"Evento {event_type.value} publicado",
            extra={"event": event}
        )
        
    async def _notify_handler(self, handler: EventHandler, event: Dict[str, Any]):
        """Notifica um handler específico sobre um evento"""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Erro ao notificar handler: {e}",
                extra={"event": event},
                exc_info=True
            )
            
    async def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retorna histórico de eventos"""
        async with self._lock:
            history = self._event_history
            if event_type:
                history = [
                    event for event in history
                    if event["type"] == event_type.value
                ]
            if limit:
                history = history[-limit:]
            return history.copy()
            
    async def clear_history(self):
        """Limpa histórico de eventos"""
        async with self._lock:
            self._event_history.clear()
            
class EmbateEventManager:
    """Gerenciador de eventos específico para embates"""
    
    def __init__(self):
        self.event_manager = EventManager()
        
    async def on_embate_started(
        self,
        embate_id: str,
        context: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica início de um embate"""
        await self.event_manager.publish(
            EventType.EMBATE_STARTED,
            {
                "embate_id": embate_id,
                "context": context
            },
            metadata
        )
        
    async def on_embate_completed(
        self,
        embate_id: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica conclusão de um embate"""
        await self.event_manager.publish(
            EventType.EMBATE_COMPLETED,
            {
                "embate_id": embate_id,
                "result": result
            },
            metadata
        )
        
    async def on_embate_failed(
        self,
        embate_id: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica falha em um embate"""
        await self.event_manager.publish(
            EventType.EMBATE_FAILED,
            {
                "embate_id": embate_id,
                "error": str(error),
                "error_type": error.__class__.__name__
            },
            metadata
        )
        
    async def on_agent_started(
        self,
        agent_id: str,
        embate_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica início de processamento por um agente"""
        await self.event_manager.publish(
            EventType.AGENT_STARTED,
            {
                "agent_id": agent_id,
                "embate_id": embate_id
            },
            metadata
        )
        
    async def on_agent_completed(
        self,
        agent_id: str,
        embate_id: str,
        result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica conclusão de processamento por um agente"""
        await self.event_manager.publish(
            EventType.AGENT_COMPLETED,
            {
                "agent_id": agent_id,
                "embate_id": embate_id,
                "result": result
            },
            metadata
        )
        
    async def on_agent_failed(
        self,
        agent_id: str,
        embate_id: str,
        error: Exception,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notifica falha no processamento por um agente"""
        await self.event_manager.publish(
            EventType.AGENT_FAILED,
            {
                "agent_id": agent_id,
                "embate_id": embate_id,
                "error": str(error),
                "error_type": error.__class__.__name__
            },
            metadata
        )
        
    async def subscribe_to_embate(
        self,
        embate_id: str,
        handler: EventHandler
    ):
        """Registra handler para eventos de um embate específico"""
        async def filtered_handler(event: Dict[str, Any]):
            if event["data"].get("embate_id") == embate_id:
                await handler(event)
                
        for event_type in [
            EventType.EMBATE_STARTED,
            EventType.EMBATE_COMPLETED,
            EventType.EMBATE_FAILED,
            EventType.AGENT_STARTED,
            EventType.AGENT_COMPLETED,
            EventType.AGENT_FAILED
        ]:
            await self.event_manager.subscribe(event_type, filtered_handler)
            
    async def get_embate_history(
        self,
        embate_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Retorna histórico de eventos de um embate específico"""
        history = await self.event_manager.get_history()
        filtered_history = [
            event for event in history
            if event["data"].get("embate_id") == embate_id
        ]
        if limit:
            filtered_history = filtered_history[-limit:]
        return filtered_history 