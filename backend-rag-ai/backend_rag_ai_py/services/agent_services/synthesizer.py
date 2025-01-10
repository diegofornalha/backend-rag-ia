"""
Agente responsável por sintetizar e consolidar informações.
"""

from typing import Any, Dict

from ..llm_services.providers.gemini import GeminiProvider


class SynthesizerAgent:
    """Agente sintetizador."""

    def __init__(self, provider: GeminiProvider):
        """Inicializa o agente."""
        self.provider = provider

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Processa uma tarefa de síntese.

        Args:
            context: Contexto da tarefa

        Returns:
            dict: Resultado da síntese
        """
        try:
            # Prepara prompt de síntese
            synthesis_prompt = f"""
            Por favor, sintetize as seguintes informações:
            
            Pesquisa:
            {context.get('research', '')}
            
            Análise:
            {context.get('analysis', '')}
            
            Melhorias:
            {context.get('improvements', '')}
            
            Forneça:
            1. Resumo executivo
            2. Principais conclusões
            3. Próximos passos recomendados
            """

            # Gera síntese
            synthesis = await self.provider.generate_content(synthesis_prompt)

            return {
                "synthesis": synthesis,
                "status": "success"
            }

        except Exception as e:
            return {"error": f"Erro na síntese: {str(e)}"} 