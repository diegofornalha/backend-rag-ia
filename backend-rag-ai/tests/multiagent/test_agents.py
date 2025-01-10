"""
Testes para os agentes do sistema multiagente.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend_rag_ia.services.multiagent.agents import (
    ResearcherAgent,
    AnalystAgent,
    ImproverAgent,
    SynthesizerAgent
)
from backend_rag_ia.services.multiagent.core.providers import GeminiProvider

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

@pytest.mark.asyncio
async def test_researcher_agent(mock_provider):
    """Testa o agente pesquisador."""
    # Configura mock
    mock_provider.generate_content.return_value = "Resultado da pesquisa"
    
    # Cria agente
    agent = ResearcherAgent(mock_provider)
    
    # Executa teste
    response = await agent.process("Pesquisar sobre IA")
    
    # Verifica resultado
    assert response.status == "success"
    assert response.result == "Resultado da pesquisa"
    assert response.agent == "researcher"
    mock_provider.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_analyst_agent(mock_provider):
    """Testa o agente analista."""
    # Configura mock
    mock_provider.analyze_content.return_value = "Resultado da análise"
    
    # Cria agente
    agent = AnalystAgent(mock_provider)
    
    # Executa teste
    response = await agent.process("Analisar dados")
    
    # Verifica resultado
    assert response.status == "success"
    assert response.result == "Resultado da análise"
    assert response.agent == "analyst"
    mock_provider.analyze_content.assert_called_once()

@pytest.mark.asyncio
async def test_improver_agent(mock_provider):
    """Testa o agente melhorador."""
    # Configura mock
    mock_provider.generate_content.return_value = "Conteúdo melhorado"
    
    # Cria agente
    agent = ImproverAgent(mock_provider)
    
    # Executa teste
    response = await agent.process("Melhorar texto")
    
    # Verifica resultado
    assert response.status == "success"
    assert response.result == "Conteúdo melhorado"
    assert response.agent == "improver"
    mock_provider.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_synthesizer_agent(mock_provider):
    """Testa o agente sintetizador."""
    # Configura mock
    mock_provider.generate_content.return_value = "Síntese do conteúdo"
    
    # Cria agente
    agent = SynthesizerAgent(mock_provider)
    
    # Executa teste
    response = await agent.process("Sintetizar informações")
    
    # Verifica resultado
    assert response.status == "success"
    assert response.result == "Síntese do conteúdo"
    assert response.agent == "synthesizer"
    mock_provider.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_agent_error_handling(mock_provider):
    """Testa tratamento de erros dos agentes."""
    # Configura mock para lançar erro
    async def mock_error(*args, **kwargs):
        raise Exception("Erro de teste")
        
    mock_provider.generate_content = MagicMock(side_effect=mock_error)
    mock_provider.analyze_content = MagicMock(side_effect=mock_error)
    
    # Testa cada agente
    agents = [
        ResearcherAgent(mock_provider),
        AnalystAgent(mock_provider),
        ImproverAgent(mock_provider),
        SynthesizerAgent(mock_provider)
    ]
    
    for agent in agents:
        # Executa teste
        response = await agent.process("Tarefa com erro")
        
        # Verifica resultado
        assert response.status == "error"
        assert "Erro de teste" in response.error
        assert response.agent == agent.name 