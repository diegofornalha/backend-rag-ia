"""
Base para os agentes do sistema.
"""

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from ..llm_services.tracker import LlmTracker
from ...analysis.suggestions.interfaces import CursorAI

class AgentCoordinator:
    """Coordenador base do sistema multiagente."""
    
    def __init__(self):
        """Inicializa o coordenador."""
        self.agents = {}
        self.tasks = []
        self.status = "initialized"
    
    async def process(
        self,
        context: Dict[str, Any],
        initial_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa uma tarefa usando os agentes disponíveis."""
        try:
            self.status = "processing"
            
            # Valida o contexto
            if not context.get("model") or not context.get("tracker"):
                raise ValueError("Contexto inválido: model e tracker são obrigatórios")
            
            # Registra início do processamento
            if isinstance(context["tracker"], LlmTracker):
                context["tracker"].track_event("process_start", {
                    "context": str(context),
                    "initial_analysis": str(initial_analysis)
                })
            
            # Executa análise inicial se não fornecida
            if not initial_analysis:
                cursor_ai = CursorAI()
                analysis_result = await cursor_ai.analyze(context)
                initial_analysis = {
                    "capabilities": analysis_result.metadata.get("capabilities", []),
                    "findings": analysis_result.findings,
                    "recommendations": analysis_result.recommendations
                }
            
            # Coordena processamento entre agentes
            tasks = []
            for capability in initial_analysis["capabilities"]:
                if agent := self.agents.get(capability):
                    tasks.append(
                        asyncio.create_task(
                            agent.process(context)
                        )
                    )
            
            # Aguarda resultados
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            else:
                results = []
            
            # Consolida resultados
            consolidated = {
                "status": "success",
                "results": results,
                "metadata": {
                    "agents_used": len(tasks),
                    "initial_analysis": initial_analysis
                }
            }
            
            # Registra conclusão
            if isinstance(context["tracker"], LlmTracker):
                context["tracker"].track_event("process_complete", consolidated)
            
            self.status = "idle"
            return consolidated
            
        except Exception as e:
            self.status = "error"
            if isinstance(context.get("tracker"), LlmTracker):
                context["tracker"].track_event("process_error", {"error": str(e)})
            raise
    
    async def generate(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera uma resposta usando os agentes disponíveis."""
        try:
            self.status = "generating"
            
            # Valida contexto
            if not context.get("model"):
                raise ValueError("Contexto inválido: model é obrigatório")
            
            # Registra início
            if isinstance(context.get("tracker"), LlmTracker):
                context["tracker"].track_event("generate_start", {"context": str(context)})
            
            # Prepara geração
            cursor_ai = CursorAI()
            analysis_result = await cursor_ai.analyze(context)
            
            # Configura geração
            generation_config = {}
            if "generation" in analysis_result.metadata:
                generation_config = analysis_result.metadata["generation"]
            
            # Gera resposta
            response = await context["model"].generate_content(
                str(context.get("input_context")),
                context={"generation_config": generation_config}
            )
            
            result = {
                "status": "success",
                "response": response,
                "metadata": {
                    "analysis": {
                        "findings": analysis_result.findings,
                        "recommendations": analysis_result.recommendations
                    },
                    "model": context["model"].config["model"]["name"]
                }
            }
            
            # Registra conclusão
            if isinstance(context.get("tracker"), LlmTracker):
                context["tracker"].track_event("generate_complete", result)
            
            self.status = "idle"
            return result
            
        except Exception as e:
            self.status = "error"
            if isinstance(context.get("tracker"), LlmTracker):
                context["tracker"].track_event("generate_error", {"error": str(e)})
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do coordenador."""
        return {
            "status": self.status,
            "active_agents": len(self.agents),
            "pending_tasks": len(self.tasks)
        }
    
    def register_agent(self, capability: str, agent: Any) -> None:
        """Registra um agente para uma capacidade específica."""
        self.agents[capability] = agent 