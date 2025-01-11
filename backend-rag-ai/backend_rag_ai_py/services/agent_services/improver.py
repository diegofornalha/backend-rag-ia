"""
Agente responsável por melhorar e refinar conteúdo.
"""

from typing import Any, Dict

from ..llm_services.providers.gemini import GeminiProvider


class ImproverAgent:
    """Agente melhorador."""

    def __init__(self, provider: GeminiProvider):
        """Inicializa o agente."""
        self.provider = provider

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Processa uma tarefa de melhoria.

        Args:
            context: Contexto da tarefa

        Returns:
            dict: Resultado da melhoria
        """
        try:
            # Prepara prompt de melhoria
            improvement_prompt = f"""
            Por favor, melhore o seguinte conteúdo:
            
            {context.get('analysis', '')}
            
            Forneça:
            1. Sugestões de melhoria
            2. Exemplos práticos
            3. Recomendações específicas
            """

            # Gera melhorias
            improvements = await self.provider.generate_content(improvement_prompt)

            return {
                "improvements": improvements,
                "status": "success"
            }

        except Exception as e:
            return {"error": f"Erro na melhoria: {str(e)}"} 