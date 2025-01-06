"""
Agente responsável por sintetizar informações.
"""

from typing import Any, Dict, Optional

from ..core.interfaces import Agent, AgentResponse
from ..core.logging import get_multiagent_logger
from ..core.providers import GeminiProvider

logger = get_multiagent_logger(__name__)


class SynthesizerAgent(Agent):
    """Agente que sintetiza e consolida informações."""

    def __init__(self, provider: GeminiProvider):
        """
        Inicializa o agente.

        Args:
            provider: Provedor LLM para processamento
        """
        self.provider = provider
        self.name = "synthesizer"
        self.description = "Agente que sintetiza e consolida informações"

    async def process(self, task: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """
        Processa uma tarefa de síntese.

        Args:
            task: Descrição da tarefa
            context: Contexto opcional

        Returns:
            Resultado do processamento
        """
        try:
            # Prepara prompt de síntese
            synthesis_prompt = f"""
            Por favor, sintetize as seguintes informações:
            
            {task}
            
            Forneça:
            1. Resumo executivo
            2. Principais conclusões
            3. Recomendações finais
            """

            # Executa síntese
            result = await self.provider.generate_content(synthesis_prompt)

            return AgentResponse(agent=self.name, status="success", result=result)

        except Exception as e:
            logger.error(f"Erro ao processar tarefa: {e}")
            return AgentResponse(agent=self.name, status="error", error=str(e))
