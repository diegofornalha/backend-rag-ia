from typing import Dict, Any
from datetime import datetime

from .base_strategy import EmbateStrategy
from ..metrics.embate_metrics import MetricsService
from ..metrics.render_metrics import RenderMetrics
from ..containment.containment_service import ContainmentService
from ..logging.render_logger import RenderLogger
from ..cache.cache_manager import EmbateCache
from ..events.event_manager import EmbateEventManager

class MultiagentStrategy(EmbateStrategy):
    """Estratégia para embates usando sistema multiagente"""
    
    def __init__(self):
        self.metrics_service = MetricsService()
        self.render_metrics = RenderMetrics()
        self.containment_service = ContainmentService()
        self.logger = RenderLogger("multiagent_embates")
        self.cache = EmbateCache()
        self.event_manager = EmbateEventManager()
        self.start_time = datetime.utcnow()
        
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um embate usando múltiplos agentes"""
        embate_id = context.get("embate_id")
        
        self.logger.info(
            "Iniciando processamento de embate",
            {"embate_id": embate_id, "context": context}
        )
        
        await self.event_manager.notify_started(embate_id, context)
        
        # Verifica cache primeiro
        cached_result = await self.cache.get_result(embate_id)
        if cached_result:
            self.logger.info(
                "Resultado encontrado no cache",
                {"embate_id": embate_id}
            )
            await self.event_manager.notify_cache_result(embate_id, True, context)
            return cached_result
            
        await self.event_manager.notify_cache_result(embate_id, False, context)
        
        # Verifica limites e cooldown
        if not await self.containment_service.check_rate_limit(embate_id):
            await self.containment_service.set_cooldown(embate_id)
            self.logger.warning(
                "Limite de taxa excedido",
                {"embate_id": embate_id}
            )
            await self.event_manager.notify_rate_limited(embate_id)
            raise ValueError("Limite de taxa excedido")
            
        try:
            # Processamento do embate
            result = await self._process_multiagent(context)
            
            # Registra métricas locais
            response_time = (datetime.utcnow() - self.start_time).total_seconds()
            tokens_used = result.get("tokens_used", 0)
            
            self.metrics_service.record_call(
                embate_id=embate_id,
                success=True,
                response_time=response_time,
                tokens_used=tokens_used
            )
            
            # Registra métricas no Render
            await self.render_metrics.record_histogram(
                "embate_response_time",
                response_time
            )
            await self.render_metrics.record_counter(
                "embate_tokens_used",
                tokens_used
            )
            await self.render_metrics.record_counter(
                "embate_success_total"
            )
            
            # Armazena resultado no cache
            await self.cache.set_result(embate_id, result)
            
            self.logger.info(
                "Embate processado com sucesso",
                {
                    "embate_id": embate_id,
                    "response_time": response_time,
                    "tokens_used": tokens_used
                }
            )
            
            # Notifica conclusão
            metrics = await self.get_metrics()
            await self.event_manager.notify_completed(embate_id, result, metrics)
            
            return result
            
        except Exception as e:
            # Registra métricas de falha
            response_time = (datetime.utcnow() - self.start_time).total_seconds()
            
            self.metrics_service.record_call(
                embate_id=embate_id,
                success=False,
                response_time=response_time,
                tokens_used=0
            )
            
            await self.render_metrics.record_counter("embate_failure_total")
            
            self.logger.error(
                "Erro no processamento do embate",
                {
                    "embate_id": embate_id,
                    "error": str(e),
                    "response_time": response_time
                }
            )
            
            # Notifica falha
            await self.event_manager.notify_failed(embate_id, str(e), context)
            
            raise e
            
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida o contexto para embate multiagente"""
        required_fields = ["embate_id", "task", "config"]
        is_valid = all(field in context for field in required_fields)
        
        if not is_valid:
            self.logger.warning(
                "Contexto inválido para embate",
                {
                    "context": context,
                    "missing_fields": [f for f in required_fields if f not in context]
                }
            )
            
        return is_valid
        
    async def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do embate multiagente"""
        metrics = {
            "success_rate": self.metrics_service.get_success_rate("multiagent"),
            "calls_per_minute": self.metrics_service.get_calls_per_minute("multiagent"),
            "total_tokens": self.metrics_service.get_metrics("multiagent").total_tokens_used
        }
        
        # Registra métricas no dashboard do Render
        await self.render_metrics.record_gauge(
            "embate_success_rate",
            metrics["success_rate"]
        )
        await self.render_metrics.record_gauge(
            "embate_calls_per_minute",
            metrics["calls_per_minute"]
        )
        
        return metrics
        
    async def _process_multiagent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implementação específica do processamento multiagente"""
        # TODO: Implementar lógica específica do multiagente
        # Esta é uma implementação temporária
        return {
            "status": "success",
            "tokens_used": 100,
            "results": {
                "agent1": {"response": "Resposta do agente 1"},
                "agent2": {"response": "Resposta do agente 2"}
            }
        } 