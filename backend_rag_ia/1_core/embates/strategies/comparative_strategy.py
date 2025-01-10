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

class ComparativeStrategy(IEmbateStrategy):
    """Estratégia para comparar múltiplas opções e escolher a melhor"""
    
    @property
    def strategy_name(self) -> str:
        return "comparative"
        
    async def validate(self, context: EmbateContext) -> bool:
        """Valida contexto para estratégia comparativa"""
        required_params = [
            "options",  # Lista de opções a comparar
            "criteria", # Critérios de comparação
            "weights",  # Pesos para cada critério
            "agent",    # Agente que fará a análise
            "prompt_template"
        ]
        return all(param in context.parameters for param in required_params)
        
    async def process(
        self,
        context: EmbateContext,
        cache: IEmbateCache,
        events: IEmbateEvents
    ) -> EmbateResult:
        """Processa embate comparativo"""
        try:
            # Extrai parâmetros
            options = context.parameters["options"]
            criteria = context.parameters["criteria"]
            weights = context.parameters["weights"]
            agent = context.parameters["agent"]
            prompt_template = context.parameters["prompt_template"]
            
            # Inicializa resultado
            result = DefaultEmbateResult(
                _embate_id=context.embate_id,
                _success=True,
                _data={},
                _metrics={},
                _errors=[]
            )
            
            # Análise individual de cada opção
            individual_scores = {}
            for option in options:
                try:
                    # Notifica análise da opção
                    await events.on_agent_started(
                        agent_id="comparative_analyzer",
                        embate_id=context.embate_id,
                        metadata={"option": option}
                    )
                    
                    # Prepara prompt para análise individual
                    prompt = self._prepare_individual_prompt(
                        prompt_template,
                        option,
                        criteria
                    )
                    
                    # Executa análise
                    analysis = await self._execute_agent(
                        agent,
                        prompt,
                        context.parameters
                    )
                    
                    # Valida e normaliza scores
                    scores = self._normalize_scores(
                        analysis.get("scores", {}),
                        criteria
                    )
                    
                    individual_scores[option] = {
                        "scores": scores,
                        "analysis": analysis.get("analysis", {})
                    }
                    
                    # Notifica conclusão da análise
                    await events.on_agent_completed(
                        agent_id="comparative_analyzer",
                        embate_id=context.embate_id,
                        result={"option": option, "scores": scores},
                        metadata={"phase": "individual_analysis"}
                    )
                    
                except Exception as e:
                    result.add_error(e)
                    await events.on_agent_failed(
                        agent_id="comparative_analyzer",
                        embate_id=context.embate_id,
                        error=e,
                        metadata={"option": option}
                    )
                    
            # Calcula scores finais ponderados
            final_scores = self._calculate_weighted_scores(
                individual_scores,
                weights
            )
            
            # Determina melhor opção
            best_option = max(
                final_scores.items(),
                key=lambda x: x[1]["final_score"]
            )
            
            # Prepara resultado final
            result.update_data({
                "individual_analysis": individual_scores,
                "final_scores": final_scores,
                "best_option": {
                    "option": best_option[0],
                    "score": best_option[1]["final_score"],
                    "analysis": best_option[1]["analysis"]
                }
            })
            
            # Adiciona métricas
            result.add_metric("options_analyzed", len(options))
            result.add_metric("criteria_used", len(criteria))
            result.add_metric(
                "score_spread",
                max(s["final_score"] for s in final_scores.values()) -
                min(s["final_score"] for s in final_scores.values())
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento comparativo: {e}")
            return DefaultEmbateResult.error_result(
                context.embate_id,
                e
            )
            
    def _prepare_individual_prompt(
        self,
        template: str,
        option: str,
        criteria: List[str]
    ) -> str:
        """Prepara prompt para análise individual"""
        try:
            return template.format(
                option=option,
                criteria="\n".join(f"- {c}" for c in criteria)
            )
        except Exception as e:
            raise ValueError(f"Erro ao preparar prompt: {e}")
            
    async def _execute_agent(
        self,
        agent: Any,
        prompt: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa agente para análise"""
        try:
            result = await agent.execute(
                prompt=prompt,
                **parameters.get("agent_parameters", {})
            )
            
            if not isinstance(result, dict):
                raise ValueError(f"Resultado inválido do agente: {result}")
                
            return result
            
        except Exception as e:
            raise RuntimeError(f"Erro na execução do agente: {e}")
            
    def _normalize_scores(
        self,
        scores: Dict[str, float],
        criteria: List[str]
    ) -> Dict[str, float]:
        """Normaliza scores para escala 0-1"""
        normalized = {}
        for criterion in criteria:
            score = scores.get(criterion, 0.0)
            # Garante que score está entre 0 e 1
            normalized[criterion] = max(0.0, min(1.0, score))
        return normalized
        
    def _calculate_weighted_scores(
        self,
        individual_scores: Dict[str, Dict[str, Any]],
        weights: Dict[str, float]
    ) -> Dict[str, Dict[str, Any]]:
        """Calcula scores finais ponderados"""
        final_scores = {}
        
        # Normaliza pesos
        total_weight = sum(weights.values())
        normalized_weights = {
            k: w/total_weight for k, w in weights.items()
        }
        
        for option, data in individual_scores.items():
            scores = data["scores"]
            weighted_sum = sum(
                scores.get(criterion, 0.0) * normalized_weights.get(criterion, 0.0)
                for criterion in weights.keys()
            )
            
            final_scores[option] = {
                "final_score": weighted_sum,
                "weighted_scores": {
                    criterion: scores.get(criterion, 0.0) * normalized_weights.get(criterion, 0.0)
                    for criterion in weights.keys()
                },
                "analysis": data["analysis"]
            }
            
        return final_scores 