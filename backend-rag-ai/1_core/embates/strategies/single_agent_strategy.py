from typing import Dict, Any, Optional
import logging
from ..interfaces.embate_interfaces import (
    IEmbateStrategy,
    EmbateContext,
    EmbateResult,
    IEmbateCache,
    IEmbateEvents
)
from ..models.embate_models import DefaultEmbateResult

logger = logging.getLogger(__name__)

class SingleAgentStrategy(IEmbateStrategy):
    """Estratégia de embate usando um único agente"""
    
    @property
    def strategy_name(self) -> str:
        return "single_agent"
        
    async def validate(self, context: EmbateContext) -> bool:
        """Valida contexto para estratégia de agente único"""
        required_params = ["agent", "prompt_template"]
        return all(param in context.parameters for param in required_params)
        
    async def process(
        self,
        context: EmbateContext,
        cache: IEmbateCache,
        events: IEmbateEvents
    ) -> EmbateResult:
        """Processa embate usando um único agente"""
        try:
            # Extrai parâmetros
            agent = context.parameters["agent"]
            prompt_template = context.parameters["prompt_template"]
            parameters = context.parameters.get("agent_parameters", {})
            
            # Notifica início do agente
            await events.on_agent_started(
                agent_id="single_agent",
                embate_id=context.embate_id,
                metadata=context.metadata
            )
            
            # Prepara prompt
            prompt = self._prepare_prompt(
                prompt_template,
                context.parameters
            )
            
            # Executa agente
            result = await self._execute_agent(
                agent,
                prompt,
                parameters,
                context.parameters
            )
            
            # Cria resultado
            embate_result = DefaultEmbateResult(
                _embate_id=context.embate_id,
                _success=True,
                _data=result,
                _metrics={
                    "tokens_used": result.get("tokens_used", 0),
                    "processing_time": result.get("processing_time", 0)
                },
                _errors=[]
            )
            
            # Notifica conclusão do agente
            await events.on_agent_completed(
                agent_id="single_agent",
                embate_id=context.embate_id,
                result=result,
                metadata=context.metadata
            )
            
            return embate_result
            
        except Exception as e:
            logger.error(f"Erro no processamento com agente único: {e}")
            
            # Notifica falha do agente
            await events.on_agent_failed(
                agent_id="single_agent",
                embate_id=context.embate_id,
                error=e,
                metadata=context.metadata
            )
            
            return DefaultEmbateResult.error_result(
                context.embate_id,
                e
            )
            
    def _prepare_prompt(
        self,
        template: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Prepara prompt para o agente"""
        try:
            return template.format(**parameters)
        except Exception as e:
            raise ValueError(f"Erro ao preparar prompt: {e}")
            
    async def _execute_agent(
        self,
        agent: Any,
        prompt: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa o agente"""
        try:
            # Executa agente com timeout
            result = await agent.execute(
                prompt=prompt,
                context=context,
                **parameters
            )
            
            # Valida resultado
            if not isinstance(result, dict):
                raise ValueError(f"Resultado inválido do agente: {result}")
                
            return result
            
        except Exception as e:
            raise RuntimeError(f"Erro na execução do agente: {e}") 