"""
Sistema multiagente para coordenação de tarefas.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging

from ...engine.llms.gemini_config import get_model_config, GENERATION_CONFIG
from ...engine.llms.tracker import LlmTracker
from ...analysis.suggestions.interfaces import CursorAI

logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """Sistema multiagente para coordenação de tarefas."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa o sistema multiagente."""
        self.config = config or get_model_config()
        self.agents: List[CursorAI] = []
        self.tracker = LlmTracker()
        self._setup_agents()
    
    def _setup_agents(self) -> None:
        """Configura os agentes do sistema."""
        # Adiciona agente principal
        self.agents.append(CursorAI())
        
        # Configura logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    async def process_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa uma tarefa usando os agentes."""
        try:
            # Registra início
            self.tracker.track_event("task_start", {
                "task": task,
                "context": str(context)
            })
            
            # Prepara contexto
            task_context = {
                "task": task,
                "config": self.config,
                "generation_config": GENERATION_CONFIG
            }
            if context:
                task_context.update(context)
            
            # Processa com agentes
            tasks = []
            for agent in self.agents:
                tasks.append(
                    asyncio.create_task(
                        agent.process(task_context)
                    )
                )
            
            # Aguarda resultados
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Consolida resultados
            response = {
                "status": "success",
                "results": results,
                "metadata": {
                    "agents_used": len(tasks),
                    "config": self.config["model"]
                }
            }
            
            # Registra conclusão
            self.tracker.track_event("task_complete", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento da tarefa: {str(e)}")
            self.tracker.track_event("task_error", {"error": str(e)})
            raise
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gera uma resposta usando os agentes."""
        try:
            # Registra início
            self.tracker.track_event("generate_start", {
                "prompt": prompt,
                "context": str(context)
            })
            
            # Prepara contexto
            gen_context = {
                "prompt": prompt,
                "config": self.config,
                "generation_config": GENERATION_CONFIG
            }
            if context:
                gen_context.update(context)
            
            # Gera com agente principal
            agent = self.agents[0]
            result = await agent.generate(gen_context)
            
            response = {
                "status": "success",
                "response": result,
                "metadata": {
                    "model": self.config["model"]["name"],
                    "temperature": self.config["model"]["temperature"]
                }
            }
            
            # Registra conclusão
            self.tracker.track_event("generate_complete", response)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro na geração de resposta: {str(e)}")
            self.tracker.track_event("generate_error", {"error": str(e)})
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna o status atual do sistema."""
        return {
            "active_agents": len(self.agents),
            "config": {
                "model": self.config["model"]["name"],
                "temperature": self.config["model"]["temperature"]
            },
            "metrics": self.tracker.get_metrics()
        } 