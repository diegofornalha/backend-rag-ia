"""
Testes para o exemplo do sistema multiagente.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend_rag_ai_py.examples.multiagent_example import process_research_task
from backend_rag_ai_py.services.multiagent.core.coordinator import AgentCoordinator
from backend_rag_ai_py.services.multiagent.core.providers import GeminiProvider

@pytest.fixture
def mock_provider():
    """Mock do provedor LLM."""
    provider = MagicMock(spec=GeminiProvider)
    
    # Configura métodos assíncronos
    async def mock_generate(*args, **kwargs):
        return provider.generate_content.return_value
        
    async def mock_analyze(*args, **kwargs):
        return provider.analyze_content.return_value
        
    provider.generate_content = MagicMock(side_effect=mock_generate)
    provider.analyze_content = MagicMock(side_effect=mock_analyze)
    
    return provider

@pytest.fixture
def coordinator(mock_provider):
    """Coordenador para testes."""
    return AgentCoordinator(mock_provider)

@pytest.mark.asyncio
async def test_process_research_task(coordinator, mock_provider):
    """Testa processamento de tarefa de pesquisa."""
    # Configura mocks
    results = [
        "Resultado da pesquisa sobre IA na saúde",
        "Análise dos impactos e tendências",
        "Conteúdo melhorado e estruturado",
        "Síntese final das descobertas"
    ]
    
    async def mock_generate(*args, **kwargs):
        return results.pop(0)
        
    async def mock_analyze(*args, **kwargs):
        return results.pop(0)
        
    mock_provider.generate_content = MagicMock(side_effect=mock_generate)
    mock_provider.analyze_content = MagicMock(side_effect=mock_analyze)
    
    # Define tarefa
    task = """
    Pesquise sobre o impacto da Inteligência Artificial na área da saúde,
    considerando os seguintes aspectos:
    1. Principais aplicações atuais
    2. Benefícios e riscos
    3. Tendências futuras
    4. Desafios éticos
    """
    
    # Executa teste
    results = await process_research_task(coordinator, task)
    
    # Verifica resultados
    assert len(results) == 4
    assert all(r.status == "success" for r in results)
    
    # Verifica sequência de agentes
    assert results[0].agent == "researcher"
    assert results[1].agent == "analyst"
    assert results[2].agent == "improver"
    assert results[3].agent == "synthesizer"
    
    # Verifica conteúdo
    assert "pesquisa" in results[0].result.lower()
    assert "análise" in results[1].result.lower()
    assert "melhorado" in results[2].result.lower()
    assert "síntese" in results[3].result.lower() 