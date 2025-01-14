"""
Classe base para agentes usando Gemini.
"""

import logging
import google.generativeai as genai
from typing import Any

logger = logging.getLogger(__name__)

class GeminiAgent:
    """Agente base usando Gemini."""

    def __init__(self, name: str, api_key: str):
        self.name = name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    async def run(self, task: str, **kwargs) -> dict[str, Any]:
        """Executa uma tarefa usando Gemini."""
        try:
            response = self.model.generate_content(task)
            return {"result": response.text}
        except Exception as e:
            logger.error(f"Erro ao executar tarefa: {e}")
            return {"error": str(e)} 