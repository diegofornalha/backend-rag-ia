from typing import Dict, Any, List
from datetime import datetime
import logging
import google.generativeai as genai

from .base_strategy import EmbateStrategy
from ..metrics.embate_metrics import MetricsService
from ..metrics.render_metrics import RenderMetrics
from ..containment.containment_service import ContainmentService
from ..logging.render_logger import RenderLogger
from ..cache.cache_manager import EmbateCache
from ..events.event_manager import EmbateEventManager

logger = logging.getLogger(__name__)

class ComparativeStrategy(EmbateStrategy):
    """Estratégia para embates focados em comparação e análise"""
    
    def __init__(self):
        self.metrics_service = MetricsService()
        self.render_metrics = RenderMetrics()
        self.containment_service = ContainmentService()
        self.logger = RenderLogger("comparative_embates")
        self.cache = EmbateCache()
        self.event_manager = EmbateEventManager()
        self.start_time = datetime.utcnow()
        
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um embate comparativo"""
        embate_id = context.get("embate_id")
        task = context.get("task", "")
        items = context.get("items", [])
        
        if not items:
            raise ValueError("Items para comparação não fornecidos")
            
        self.logger.info(
            "Iniciando análise comparativa",
            {"embate_id": embate_id, "items": items}
        )
        
        await self.event_manager.notify_started(embate_id, context)
        
        # Verifica cache
        cached_result = await self.cache.get_result(embate_id)
        if cached_result:
            self.logger.info("Resultado encontrado no cache", {"embate_id": embate_id})
            await self.event_manager.notify_cache_result(embate_id, True, context)
            return cached_result
            
        await self.event_manager.notify_cache_result(embate_id, False, context)
        
        # Verifica limites
        if not await self.containment_service.check_rate_limit(embate_id):
            await self.containment_service.set_cooldown(embate_id)
            self.logger.warning("Limite de taxa excedido", {"embate_id": embate_id})
            await self.event_manager.notify_rate_limited(embate_id)
            raise ValueError("Limite de taxa excedido")
            
        try:
            # Realiza análise comparativa
            result = await self._compare_items(task, items)
            
            # Registra métricas
            response_time = (datetime.utcnow() - self.start_time).total_seconds()
            tokens_used = result.get("tokens_used", 0)
            
            self.metrics_service.record_call(
                embate_id=embate_id,
                success=True,
                response_time=response_time,
                tokens_used=tokens_used
            )
            
            await self.render_metrics.record_histogram(
                "embate_response_time",
                response_time
            )
            await self.render_metrics.record_counter(
                "embate_tokens_used",
                tokens_used
            )
            await self.render_metrics.record_counter("embate_success_total")
            
            # Cache e notificações
            await self.cache.set_result(embate_id, result)
            metrics = await self.get_metrics()
            await self.event_manager.notify_completed(embate_id, result, metrics)
            
            return result
            
        except Exception as e:
            self._handle_error(embate_id, e, context)
            raise
            
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida o contexto para análise comparativa"""
        required_fields = ["embate_id", "task", "items"]
        is_valid = all(field in context for field in required_fields)
        
        if is_valid:
            items = context.get("items", [])
            is_valid = isinstance(items, list) and len(items) >= 2
            
        if not is_valid:
            self.logger.warning(
                "Contexto inválido para análise comparativa",
                {"context": context}
            )
            
        return is_valid
        
    async def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas da análise comparativa"""
        metrics = {
            "success_rate": self.metrics_service.get_success_rate("comparative"),
            "calls_per_minute": self.metrics_service.get_calls_per_minute("comparative"),
            "total_tokens": self.metrics_service.get_metrics("comparative").total_tokens_used
        }
        
        await self.render_metrics.record_gauge(
            "embate_success_rate",
            metrics["success_rate"]
        )
        await self.render_metrics.record_gauge(
            "embate_calls_per_minute",
            metrics["calls_per_minute"]
        )
        
        return metrics
        
    async def _compare_items(self, task: str, items: List[str]) -> Dict[str, Any]:
        """Realiza a análise comparativa dos itens"""
        prompt = self._prepare_comparative_prompt(task, items)
        
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            
            return {
                "status": "success",
                "tokens_used": len(response.text.split()),
                "result": response.text,
                "items_analyzed": items
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise comparativa: {e}")
            raise
            
    def _prepare_comparative_prompt(self, task: str, items: List[str]) -> str:
        """Prepara o prompt para análise comparativa"""
        items_str = "\n".join(f"- {item}" for item in items)
        
        return f"""Realize uma análise comparativa detalhada dos seguintes itens no contexto da tarefa:

Tarefa: {task}

Itens para comparação:
{items_str}

Forneça uma análise que inclua:
1. Comparação direta entre os itens
2. Pontos fortes e fracos de cada item
3. Critérios de comparação relevantes
4. Recomendações baseadas na análise
5. Conclusão e melhor escolha (se aplicável)"""
        
    def _handle_error(self, embate_id: str, error: Exception, context: Dict[str, Any]):
        """Trata erros no processamento"""
        response_time = (datetime.utcnow() - self.start_time).total_seconds()
        
        self.metrics_service.record_call(
            embate_id=embate_id,
            success=False,
            response_time=response_time,
            tokens_used=0
        )
        
        self.logger.error(
            "Erro na análise comparativa",
            {
                "embate_id": embate_id,
                "error": str(error),
                "response_time": response_time
            }
        ) 