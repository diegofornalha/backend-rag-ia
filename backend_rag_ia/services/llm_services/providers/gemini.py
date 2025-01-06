"""
Provider específico para o modelo Gemini.
"""

from typing import Any, Dict, Optional

import google.generativeai as genai

from ..gemini_config import GENERATION_CONFIG, get_model_config


class GeminiProvider:
    """Provider para interação com o modelo Gemini."""

    def __init__(self, api_key: str | None = None):
        """Inicializa o provider."""
        self.config = get_model_config()
        self.api_key = api_key
        self._setup()

    def _setup(self) -> None:
        """Configura o cliente Gemini."""
        if self.api_key:
            genai.configure(api_key=self.api_key)

        # Configura modelo
        self.model = genai.GenerativeModel(self.config["model"]["name"])

    async def generate_content(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        """Gera uma resposta usando o modelo."""
        try:
            # Prepara contexto
            generation_config = GENERATION_CONFIG.copy()
            if context and "generation_config" in context:
                generation_config.update(context["generation_config"])

            # Gera resposta
            response = self.model.generate_content(prompt, generation_config=generation_config)

            return response.text

        except Exception as e:
            raise RuntimeError(f"Erro na geração: {str(e)}")

    async def analyze(
        self, content: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analisa conteúdo usando o modelo."""
        try:
            # Prepara prompt de análise
            analysis_prompt = f"""
            Por favor, analise o seguinte conteúdo:
            
            {content}
            
            Forneça uma análise detalhada incluindo:
            1. Principais pontos
            2. Sugestões de melhoria
            3. Possíveis problemas
            """

            # Gera análise
            response = self.model.generate_content(
                analysis_prompt, generation_config=GENERATION_CONFIG
            )

            return {
                "analysis": response.text,
                "model": self.config["model"]["name"],
                "status": "success",
            }

        except Exception as e:
            raise RuntimeError(f"Erro na análise: {str(e)}")

    def get_config(self) -> dict[str, Any]:
        """Retorna a configuração atual do provider."""
        return self.config
