"""
Exemplo de uso do sistema multiagente.
"""

import asyncio
import os
from typing import List
from ..services.multiagent.core.coordinator import AgentCoordinator
from ..services.multiagent.core.providers import GeminiProvider
from ..services.multiagent.core.interfaces import AgentResponse

async def process_research_task(
    coordinator: AgentCoordinator,
    task: str
) -> List[AgentResponse]:
    """
    Processa uma tarefa de pesquisa usando o sistema multiagente.
    
    Args:
        coordinator: Coordenador dos agentes
        task: Descrição da tarefa
        
    Returns:
        Lista com resultados do processamento
    """
    # Define pipeline de agentes
    pipeline = [
        "researcher",  # Pesquisa inicial
        "analyst",     # Análise dos resultados
        "improver",    # Melhoria do conteúdo
        "synthesizer"  # Síntese final
    ]
    
    # Executa pipeline
    results = await coordinator.process_pipeline(task, pipeline)
    
    # Retorna resultados
    return results

async def main():
    """Função principal."""
    # Configura provedor
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada")
        
    provider = GeminiProvider(api_key)
    
    # Cria coordenador
    coordinator = AgentCoordinator(provider)
    
    # Define tarefa
    task = """
    Pesquise sobre o impacto da Inteligência Artificial na área da saúde,
    considerando os seguintes aspectos:
    1. Principais aplicações atuais
    2. Benefícios e riscos
    3. Tendências futuras
    4. Desafios éticos
    """
    
    try:
        # Processa tarefa
        results = await process_research_task(coordinator, task)
        
        # Exibe resultados
        print("\nResultados do processamento:")
        print("-" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Resultado do agente '{result.agent}':")
            print("-" * 30)
            
            if result.status == "success":
                print(result.result)
            else:
                print(f"Erro: {result.error}")
                
    except Exception as e:
        print(f"Erro ao processar tarefa: {e}")

if __name__ == "__main__":
    # Executa exemplo
    asyncio.run(main()) 