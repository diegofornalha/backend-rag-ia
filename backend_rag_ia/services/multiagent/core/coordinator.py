"""
Coordenador do sistema multiagente.
"""

from typing import Dict, Any, List, Optional
from .interfaces import Agent, AgentResponse
from .providers import GeminiProvider
from .logging import get_multiagent_logger
from ..agents import (
    ResearcherAgent,
    AnalystAgent,
    ImproverAgent,
    SynthesizerAgent
)

logger = get_multiagent_logger(__name__)

class AgentCoordinator:
    """Coordenador dos agentes do sistema."""
    
    def __init__(self, provider: GeminiProvider):
        """
        Inicializa o coordenador.
        
        Args:
            provider: Provedor LLM para os agentes
        """
        self.provider = provider
        
        # Inicializa agentes
        self.agents = {
            "researcher": ResearcherAgent(provider),
            "analyst": AnalystAgent(provider),
            "improver": ImproverAgent(provider),
            "synthesizer": SynthesizerAgent(provider)
        }
        
        logger.info("Coordenador inicializado com %d agentes", len(self.agents))
        
    async def process_task(
        self,
        task: str,
        agent_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Processa uma tarefa usando um agente específico.
        
        Args:
            task: Descrição da tarefa
            agent_name: Nome do agente
            context: Contexto opcional
            
        Returns:
            Resultado do processamento
        """
        # Valida agente
        if agent_name not in self.agents:
            return AgentResponse(
                agent=agent_name,
                status="error",
                error=f"Agente '{agent_name}' não encontrado"
            )
            
        # Executa tarefa
        agent = self.agents[agent_name]
        logger.info("Processando tarefa com agente %s", agent_name)
        
        try:
            return await agent.process(task, context)
            
        except Exception as e:
            logger.error("Erro ao processar tarefa: %s", e)
            return AgentResponse(
                agent=agent_name,
                status="error",
                error=str(e)
            )
            
    async def process_pipeline(
        self,
        task: str,
        pipeline: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Processa uma tarefa usando uma pipeline de agentes.
        
        Args:
            task: Descrição da tarefa
            pipeline: Lista de nomes dos agentes
            context: Contexto opcional
            
        Returns:
            Lista com resultados do processamento
        """
        results = []
        current_task = task
        current_context = context or {}
        
        # Executa cada agente na sequência
        for agent_name in pipeline:
            logger.info("Executando agente %s na pipeline", agent_name)
            
            # Processa tarefa
            result = await self.process_task(
                current_task,
                agent_name,
                current_context
            )
            
            results.append(result)
            
            # Atualiza contexto e tarefa
            if result.status == "success" and result.result:
                current_task = result.result
                current_context["previous_result"] = result.result
            else:
                # Para execução em caso de erro
                logger.error("Erro na pipeline: %s", result.error)
                break
                
        return results
        
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre um agente.
        
        Args:
            agent_name: Nome do agente
            
        Returns:
            Dicionário com informações ou None se não encontrado
        """
        if agent_name not in self.agents:
            return None
            
        agent = self.agents[agent_name]
        return {
            "name": agent_name,
            "description": agent.description
        }
        
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        Lista todos os agentes disponíveis.
        
        Returns:
            Lista com informações dos agentes
        """
        return [
            self.get_agent_info(name)
            for name in self.agents.keys()
        ] 