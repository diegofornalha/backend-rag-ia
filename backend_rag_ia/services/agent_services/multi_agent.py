"""
Sistema multiagente usando Gemini.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
import google.generativeai as genai

from ...engine.llms.gemini_config import get_model_config, GENERATION_CONFIG
from ...engine.llms.tracker import LlmTracker

logger = logging.getLogger(__name__)


class GeminiAgent:
    """Agente base usando Gemini."""

    def __init__(self, name: str, api_key: str):
        self.name = name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    async def run(self, task: str, **kwargs) -> Dict[str, Any]:
        """Executa uma tarefa usando Gemini."""
        try:
            response = self.model.generate_content(task)
            return {"result": response.text}
        except Exception as e:
            logger.error(f"Erro ao executar tarefa: {e}")
            return {"error": str(e)}


class MultiAgentSystem:
    """Sistema multiagente usando Gemini."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa o sistema multiagente."""
        self.config = config or get_model_config()
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("API key do Gemini não encontrada na configuração")

        self.agents = self._setup_agents()
        self.tracker = LlmTracker()

    def _setup_agents(self) -> Dict[str, GeminiAgent]:
        """Configura os agentes do sistema."""
        return {
            "researcher": GeminiAgent("researcher", self.api_key),
            "analyst": GeminiAgent("analyst", self.api_key),
            "improver": GeminiAgent("improver", self.api_key),
            "synthesizer": GeminiAgent("synthesizer", self.api_key),
        }

    async def process_task(
        self, task: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa uma tarefa usando o sistema multiagente."""
        try:
            # Pipeline de processamento
            pipeline = ["researcher", "analyst", "improver", "synthesizer"]
            results = {}

            for agent_name in pipeline:
                agent = self.agents[agent_name]
                result = await agent.run(task)
                results[agent_name] = result.get("result", "")

                # Atualiza contexto para próximo agente
                if result.get("result"):
                    task = result["result"]

            return results

        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {"error": str(e)}

    async def generate_response(self, prompt: str) -> Dict[str, Any]:
        """Gera uma resposta usando o agente sintetizador."""
        try:
            agent = self.agents["synthesizer"]
            result = await agent.run(prompt)
            return {"response": result.get("result", "")}

        except Exception as e:
            logger.error(f"Erro na geração: {e}")
            return {"error": str(e)}

    def get_system_status(self) -> Dict[str, Any]:
        """Retorna o status do sistema."""
        return {
            "agents": list(self.agents.keys()),
            "config": self.config,
            "tracker": self.tracker.get_metrics(),
        }
