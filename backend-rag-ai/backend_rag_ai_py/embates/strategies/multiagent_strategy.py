from typing import Dict, Any, List, Optional
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

class MultiagentStrategy(IEmbateStrategy):
    """Estratégia de embate usando múltiplos agentes"""
    
    @property
    def strategy_name(self) -> str:
        return "multiagent"
        
    async def validate(self, context: EmbateContext) -> bool:
        """Valida contexto para estratégia multiagente"""
        required_params = ["agents", "pipeline", "prompt_template"]
        return all(param in context.parameters for param in required_params)
        
    async def process(
        self,
        context: EmbateContext,
        cache: IEmbateCache,
        events: IEmbateEvents
    ) -> EmbateResult:
        """Processa embate usando múltiplos agentes"""
        try:
            # Extrai parâmetros
            agents = context.parameters["agents"]
            pipeline = context.parameters["pipeline"]
            prompt_template = context.parameters["prompt_template"]
            
            # Inicializa resultado
            result = DefaultEmbateResult(
                _embate_id=context.embate_id,
                _success=True,
                _data={},
                _metrics={},
                _errors=[]
            )
            
            # Processa pipeline de agentes
            current_context = context.parameters.get("initial_context", {})
            
            for step in pipeline:
                try:
                    # Obtém agente para o passo
                    agent = agents.get(step["agent"])
                    if not agent:
                        raise ValueError(f"Agente não encontrado: {step['agent']}")
                        
                    # Notifica início do agente
                    await events.on_agent_started(
                        agent_id=step["agent"],
                        embate_id=context.embate_id,
                        metadata={"step": step}
                    )
                    
                    # Prepara prompt
                    prompt = self._prepare_prompt(
                        prompt_template,
                        step,
                        current_context
                    )
                    
                    # Executa agente
                    agent_result = await self._execute_agent(
                        agent,
                        prompt,
                        step,
                        current_context
                    )
                    
                    # Atualiza contexto
                    current_context.update(agent_result)
                    
                    # Atualiza resultado
                    result.update_data({
                        f"step_{step['agent']}": agent_result
                    })
                    
                    # Notifica conclusão do agente
                    await events.on_agent_completed(
                        agent_id=step["agent"],
                        embate_id=context.embate_id,
                        result=agent_result,
                        metadata={"step": step}
                    )
                    
                except Exception as e:
                    # Registra erro do agente
                    result.add_error(e)
                    await events.on_agent_failed(
                        agent_id=step["agent"],
                        embate_id=context.embate_id,
                        error=e,
                        metadata={"step": step}
                    )
                    
                    # Para execução se erro for crítico
                    if step.get("critical", False):
                        break
                        
            # Finaliza resultado
            result._data["final_context"] = current_context
            result._metrics["total_steps"] = len(pipeline)
            result._metrics["completed_steps"] = len(result._data) - 1
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento multiagente: {e}")
            return DefaultEmbateResult.error_result(
                context.embate_id,
                e
            )
            
    def _prepare_prompt(
        self,
        template: str,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Prepara prompt para um agente"""
        try:
            return template.format(
                **step,
                **context,
                step_name=step["agent"]
            )
        except Exception as e:
            raise ValueError(f"Erro ao preparar prompt: {e}")
            
    async def _execute_agent(
        self,
        agent: Any,
        prompt: str,
        step: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa um agente específico"""
        try:
            # Executa agente com timeout
            result = await agent.execute(
                prompt=prompt,
                context=context,
                **step.get("parameters", {})
            )
            
            # Valida resultado
            if not isinstance(result, dict):
                raise ValueError(
                    f"Resultado inválido do agente {step['agent']}: {result}"
                )
                
            return result
            
        except Exception as e:
            raise RuntimeError(
                f"Erro na execução do agente {step['agent']}: {e}"
            )
        