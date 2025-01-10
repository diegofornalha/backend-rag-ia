"""
Agente responsável por analisar informações e identificar padrões.
"""

from typing import Any, Dict

from ..llm_services.providers.gemini import GeminiProvider


class AnalystAgent:
    """Agente analista."""

    def __init__(self, provider: GeminiProvider):
        """Inicializa o agente."""
        self.provider = provider

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Processa uma tarefa de análise.

        Args:
            context: Contexto da tarefa

        Returns:
            dict: Resultado da análise
        """
        try:
            # Prepara prompt de análise
            analysis_prompt = f"""
            Por favor, analise as seguintes informações:
            
            {context.get('research', '')}
            
            Forneça:
            1. Padrões identificados
            2. Insights principais
            3. Pontos de atenção
            """

            # Gera análise
            analysis = await self.provider.generate_content(analysis_prompt)

            return {
                "analysis": analysis,
                "status": "success"
            }

        except Exception as e:
            return {"error": f"Erro na análise: {str(e)}"} 