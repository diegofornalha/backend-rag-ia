"""
Testes para o coordenador do sistema multiagente.
"""

import pytest
from unittest.mock import MagicMock, patch

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
async def test_process_task(coordinator, mock_provider):
    """Testa processamento de tarefa."""
    # Configura mock
    mock_provider.generate_content.return_value = "Resultado do processamento"
    
    # Executa teste
    result = await coordinator.process_task(
        task="Tarefa de teste",
        agent_name="researcher"
    )
    
    # Verifica resultado
    assert result.status == "success"
    assert result.result == "Resultado do processamento"
    assert result.agent == "researcher"
    mock_provider.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_process_task_invalid_agent(coordinator):
    """Testa processamento com agente inválido."""
    result = await coordinator.process_task(
        task="Tarefa de teste",
        agent_name="invalid"
    )
    
    assert result.status == "error"
    assert "não encontrado" in result.error
    assert result.agent == "invalid"

@pytest.mark.asyncio
async def test_process_pipeline(coordinator, mock_provider):
    """Testa processamento em pipeline."""
    # Configura mocks
    results = [
        "Resultado da pesquisa",
        "Resultado da análise",
        "Resultado da melhoria",
        "Resultado da síntese"
    ]
    
    async def mock_generate(*args, **kwargs):
        return results.pop(0)
        
    async def mock_analyze(*args, **kwargs):
        return results.pop(0)
        
    mock_provider.generate_content = MagicMock(side_effect=mock_generate)
    mock_provider.analyze_content = MagicMock(side_effect=mock_analyze)
    
    # Executa teste
    pipeline_results = await coordinator.process_pipeline(
        task="Tarefa inicial",
        pipeline=["researcher", "analyst", "improver", "synthesizer"]
    )
    
    # Verifica resultados
    assert len(pipeline_results) == 4
    assert all(r.status == "success" for r in pipeline_results)
    assert pipeline_results[0].agent == "researcher"
    assert pipeline_results[1].agent == "analyst"
    assert pipeline_results[2].agent == "improver"
    assert pipeline_results[3].agent == "synthesizer"

@pytest.mark.asyncio
async def test_pipeline_error_handling(coordinator, mock_provider):
    """Testa tratamento de erros na pipeline."""
    # Configura mock para sucesso e depois erro
    results = ["Resultado da pesquisa"]
    
    async def mock_generate(*args, **kwargs):
        if not results:
            raise Exception("Erro de teste")
        return results.pop(0)
        
    mock_provider.generate_content = MagicMock(side_effect=mock_generate)
    
    # Executa teste
    pipeline_results = await coordinator.process_pipeline(
        task="Tarefa inicial",
        pipeline=["researcher", "improver", "synthesizer"]
    )
    
    # Verifica resultados
    assert len(pipeline_results) == 2  # Parou no erro
    assert pipeline_results[0].status == "success"
    assert pipeline_results[1].status == "error"
    assert "Erro de teste" in pipeline_results[1].error

def test_get_agent_info(coordinator):
    """Testa obtenção de informações do agente."""
    # Testa agente válido
    info = coordinator.get_agent_info("researcher")
    assert info is not None
    assert info["name"] == "researcher"
    assert "description" in info
    
    # Testa agente inválido
    info = coordinator.get_agent_info("invalid")
    assert info is None

def test_list_agents(coordinator):
    """Testa listagem de agentes."""
    agents = coordinator.list_agents()
    
    assert len(agents) == 4
    assert all("name" in agent for agent in agents)
    assert all("description" in agent for agent in agents)
    
    names = {agent["name"] for agent in agents}
    assert names == {"researcher", "analyst", "improver", "synthesizer"} 