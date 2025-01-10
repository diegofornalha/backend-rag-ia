"""
Provedores de modelos de linguagem.
"""

from typing import Any, Dict, Optional

import google.generativeai as genai

from .logging import get_multiagent_logger

logger = get_multiagent_logger(__name__)


class GeminiProvider:
    """Provedor do modelo Gemini."""

    def __init__(self, api_key: str):
        """
        Inicializa o provedor.

        Args:
            api_key: Chave de API do Google
        """
        if not api_key:
            raise ValueError("API key não pode estar vazia")

        self.api_key = api_key
        genai.configure(api_key=api_key)

        # Configura modelo
        self.model = genai.GenerativeModel("gemini-pro")

    async def generate_content(self, prompt: str) -> str:
        """
        Gera conteúdo usando o modelo.

        Args:
            prompt: Prompt para geração

        Returns:
            Conteúdo gerado
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo: {e}")
            raise

    async def analyze_content(self, content: str) -> str:
        """
        Analisa conteúdo usando o modelo.

        Args:
            content: Conteúdo para análise

        Returns:
            Resultado da análise
        """
        try:
            prompt = f"Analise o seguinte conteúdo:\n\n{content}"
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Erro ao analisar conteúdo: {e}")
            raise

    def get_config(self) -> dict[str, Any]:
        """
        Retorna configuração do provedor.

        Returns:
            Dicionário com configurações
        """
        return {"api_key": self.api_key}
