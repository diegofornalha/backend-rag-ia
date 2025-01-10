"""
Coordenador central do sistema multi-agente.
"""

from typing import Any, Dict, List

from ..llm_services.providers.gemini import GeminiProvider


class AgentCoordinator:
    """Coordenador dos agentes do sistema."""

    def __init__(self, provider: GeminiProvider):
        """Inicializa o coordenador."""
        self.provider = provider
        self.agents = {}

    def register_agent(self, name: str, agent: Any) -> None:
        """Registra um novo agente."""
        self.agents[name] = agent

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """Processa uma tarefa usando os agentes registrados."""
        results = {}
        for name, agent in self.agents.items():
            try:
                result = await agent.process(context)
                results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}
        return results
