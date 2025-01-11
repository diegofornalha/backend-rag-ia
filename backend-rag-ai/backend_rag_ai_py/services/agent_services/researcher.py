"""
Agente responsável por pesquisar e coletar informações.
"""

from typing import Any, Dict

from ..llm_services.providers.gemini import GeminiProvider


class ResearcherAgent:
    """Agente pesquisador."""

    def __init__(self, provider: GeminiProvider):
        """Inicializa o agente."""
        self.provider = provider

    async def process(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Processa uma tarefa de pesquisa.

        Args:
            context: Contexto da tarefa

        Returns:
            dict: Resultado da pesquisa
        """
        try:
            # Prepara prompt de pesquisa
            research_prompt = f"""
            Por favor, pesquise sobre o seguinte tópico:
            
            {context.get('query', '')}
            
            Forneça:
            1. Principais conceitos
            2. Exemplos práticos
            3. Referências relevantes
            """

            # Gera pesquisa
            research = await self.provider.generate_content(research_prompt)

            return {
                "research": research,
                "status": "success"
            }

        except Exception as e:
            return {"error": f"Erro na pesquisa: {str(e)}"} 