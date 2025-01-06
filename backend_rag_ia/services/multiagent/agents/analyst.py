"""
Agente responsável por analisar informações.
"""

from typing import Any, Dict, Optional

from ..core.interfaces import Agent, AgentResponse
from ..core.logging import get_multiagent_logger
from ..core.providers import GeminiProvider

logger = get_multiagent_logger(__name__)


class AnalystAgent(Agent):
    """Agente que analisa informações e identifica padrões."""

    def __init__(self, provider: GeminiProvider):
        """
        Inicializa o agente.

        Args:
            provider: Provedor LLM para processamento
        """
        self.provider = provider
        self.name = "analyst"
        self.description = "Agente que analisa informações e identifica padrões"

    async def process(self, task: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """
        Processa uma tarefa de análise.

        Args:
            task: Descrição da tarefa
            context: Contexto opcional

        Returns:
            Resultado do processamento
        """
        try:
            # Prepara prompt de análise
            analysis_prompt = f"""
            Por favor, analise as seguintes informações:
            
            {task}
            
            Forneça:
            1. Principais padrões identificados
            2. Insights relevantes
            3. Recomendações baseadas na análise
            """

            # Executa análise
            result = await self.provider.analyze_content(analysis_prompt)

            return AgentResponse(agent=self.name, status="success", result=result)

        except Exception as e:
            logger.error(f"Erro ao processar tarefa: {e}")
            return AgentResponse(agent=self.name, status="error", error=str(e))
