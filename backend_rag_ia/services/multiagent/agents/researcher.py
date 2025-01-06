"""
Agente responsável por pesquisar informações.
"""

from typing import Any, Dict, Optional

from ..core.interfaces import Agent, AgentResponse
from ..core.logging import get_multiagent_logger
from ..core.providers import GeminiProvider

logger = get_multiagent_logger(__name__)


class ResearcherAgent(Agent):
    """Agente que realiza pesquisas e coleta informações."""

    def __init__(self, provider: GeminiProvider):
        """
        Inicializa o agente.

        Args:
            provider: Provedor LLM para processamento
        """
        self.provider = provider
        self.name = "researcher"
        self.description = "Agente que realiza pesquisas e coleta informações"

    async def process(self, task: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """
        Processa uma tarefa de pesquisa.

        Args:
            task: Descrição da tarefa
            context: Contexto opcional

        Returns:
            Resultado do processamento
        """
        try:
            # Prepara prompt de pesquisa
            research_prompt = f"""
            Por favor, realize uma pesquisa sobre:
            
            {task}
            
            Forneça:
            1. Principais informações encontradas
            2. Fontes relevantes
            3. Pontos que merecem mais investigação
            """

            # Executa pesquisa
            result = await self.provider.generate_content(research_prompt)

            return AgentResponse(agent=self.name, status="success", result=result)

        except Exception as e:
            logger.error(f"Erro ao processar tarefa: {e}")
            return AgentResponse(agent=self.name, status="error", error=str(e))
