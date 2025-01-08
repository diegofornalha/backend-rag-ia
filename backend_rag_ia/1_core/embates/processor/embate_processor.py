from typing import Dict, Any, Optional, List
import logging
from ..interfaces.embate_interfaces import (
    IEmbateProcessor,
    IEmbateStrategy,
    EmbateContext,
    EmbateResult,
    IEmbateCache,
    IEmbateEvents,
    IEmbateMetrics,
    IEmbateLogger
)
from ..models.embate_models import DefaultEmbateResult

logger = logging.getLogger(__name__)

class EmbateProcessor(IEmbateProcessor):
    """Processador principal de embates"""
    
    def __init__(
        self,
        cache: IEmbateCache,
        events: IEmbateEvents,
        metrics: IEmbateMetrics,
        logger: IEmbateLogger
    ):
        self._cache = cache
        self._events = events
        self._metrics = metrics
        self._logger = logger
        self._strategies: Dict[str, IEmbateStrategy] = {}
        
    async def process_embate(
        self,
        context: EmbateContext,
        strategy: Optional[str] = None
    ) -> EmbateResult:
        """Processa um embate usando a estratégia especificada"""
        try:
            # Registra início do processamento
            start_time = context.created_at
            await self._events.on_embate_started(
                context.embate_id,
                context.parameters,
                context.metadata
            )
            
            # Tenta recuperar do cache
            cache_result = await self._cache.get_result(
                context.embate_id,
                context.metadata
            )
            
            if cache_result:
                self._logger.info(
                    "Resultado recuperado do cache",
                    {"embate_id": context.embate_id}
                )
                return DefaultEmbateResult(
                    _embate_id=context.embate_id,
                    _success=True,
                    _data=cache_result,
                    _metrics={"cache_hit": 1.0},
                    _errors=[]
                )
                
            # Seleciona estratégia
            strategy_impl = self._get_strategy(strategy)
            if not strategy_impl:
                raise ValueError(f"Estratégia não encontrada: {strategy}")
                
            # Valida contexto
            if not await strategy_impl.validate(context):
                raise ValueError("Contexto inválido para a estratégia")
                
            # Processa embate
            result = await strategy_impl.process(
                context,
                self._cache,
                self._events
            )
            
            # Registra métricas
            processing_time = (context.created_at - start_time).total_seconds()
            await self._metrics.record_processing_time(
                context.embate_id,
                processing_time,
                context.metadata
            )
            
            if result.success:
                await self._metrics.record_success(
                    context.embate_id,
                    context.metadata
                )
                
                # Armazena em cache
                await self._cache.store_result(
                    context.embate_id,
                    result.data,
                    metadata=context.metadata
                )
                
                # Notifica conclusão
                await self._events.on_embate_completed(
                    context.embate_id,
                    result.data,
                    context.metadata
                )
            else:
                # Registra falha
                if result.errors:
                    error = Exception(result.errors[0]["message"])
                    await self._metrics.record_failure(
                        context.embate_id,
                        error,
                        context.metadata
                    )
                    await self._events.on_embate_failed(
                        context.embate_id,
                        error,
                        context.metadata
                    )
                    
            return result
            
        except Exception as e:
            self._logger.error(
                "Erro no processamento do embate",
                error=e,
                context={"embate_id": context.embate_id}
            )
            
            # Registra falha
            await self._metrics.record_failure(
                context.embate_id,
                e,
                context.metadata
            )
            
            # Notifica falha
            await self._events.on_embate_failed(
                context.embate_id,
                e,
                context.metadata
            )
            
            return DefaultEmbateResult.error_result(
                context.embate_id,
                e
            )
            
    async def register_strategy(self, strategy: IEmbateStrategy):
        """Registra uma nova estratégia"""
        self._strategies[strategy.strategy_name] = strategy
        self._logger.info(
            f"Estratégia registrada: {strategy.strategy_name}"
        )
        
    def get_available_strategies(self) -> List[str]:
        """Retorna estratégias disponíveis"""
        return list(self._strategies.keys())
        
    def _get_strategy(self, strategy_name: Optional[str] = None) -> Optional[IEmbateStrategy]:
        """Retorna estratégia pelo nome ou a padrão"""
        if not strategy_name:
            # Usa primeira estratégia registrada como padrão
            return next(iter(self._strategies.values()), None)
            
        return self._strategies.get(strategy_name) 