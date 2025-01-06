"""
Agente responsável por melhorar conteúdo.
"""

from typing import Dict, Any, Optional
from ..core.interfaces import Agent, AgentResponse
from ..core.providers import GeminiProvider
from ..core.logging import get_multiagent_logger

logger = get_multiagent_logger(__name__)


class ImproverAgent(Agent):
    """Agente que melhora e refina conteúdo."""

    def __init__(self, provider: GeminiProvider):
        """
        Inicializa o agente.

        Args:
            provider: Provedor LLM para processamento
        """
        self.provider = provider
        self.name = "improver"
        self.description = "Agente que melhora e refina conteúdo"

    async def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """
        Processa uma tarefa de melhoria.

        Args:
            task: Descrição da tarefa
            context: Contexto opcional

        Returns:
            Resultado do processamento
        """
        try:
            # Prepara prompt de melhoria
            improvement_prompt = f"""
            Por favor, melhore o seguinte conteúdo:
            
            {task}
            
            Considere:
            1. Clareza e objetividade
            2. Estrutura e organização
            3. Completude das informações
            """

            # Executa melhoria
            result = await self.provider.generate_content(improvement_prompt)

            return AgentResponse(agent=self.name, status="success", result=result)

        except Exception as e:
            logger.error(f"Erro ao processar tarefa: {e}")
            return AgentResponse(agent=self.name, status="error", error=str(e))
