"""
Testes para o provedor Gemini.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend_rag_ia.services.multiagent.core.providers import GeminiProvider

@pytest.fixture
def mock_genai():
    """Mock do módulo google.generativeai."""
    with patch("google.generativeai") as mock:
        yield mock

@pytest.fixture
def provider(mock_genai):
    """Instância do provedor para testes."""
    provider = GeminiProvider("test_key")
    provider.model = MagicMock()
    return provider

@pytest.mark.asyncio
async def test_generate_content(provider):
    """Testa geração de conteúdo."""
    # Configura mock
    mock_response = MagicMock()
    mock_response.text = "Texto gerado"
    provider.model.generate_content = MagicMock(return_value=mock_response)
    
    # Executa teste
    result = await provider.generate_content("prompt de teste")
    
    # Verifica resultado
    assert result == "Texto gerado"
    provider.model.generate_content.assert_called_once_with("prompt de teste")

@pytest.mark.asyncio
async def test_analyze_content(provider):
    """Testa análise de conteúdo."""
    # Configura mock
    mock_response = MagicMock()
    mock_response.text = "Análise do conteúdo"
    provider.model.generate_content = MagicMock(return_value=mock_response)
    
    # Executa teste
    result = await provider.analyze_content("conteúdo para análise")
    
    # Verifica resultado
    assert result == "Análise do conteúdo"
    provider.model.generate_content.assert_called_once()

def test_get_config(provider):
    """Testa obtenção de configuração."""
    config = provider.get_config()
    assert isinstance(config, dict)
    assert "api_key" in config
    assert config["api_key"] == "test_key"

def test_invalid_api_key():
    """Testa inicialização com API key inválida."""
    with pytest.raises(ValueError):
        GeminiProvider("")  # API key vazia deve lançar ValueError 