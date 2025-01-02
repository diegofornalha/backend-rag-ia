"""Configurações específicas para testes de embates."""
import pytest
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

@pytest.fixture
def mock_supabase_response():
    """Mock de resposta do Supabase."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "arquivo": "regras_teste.md",
        "conteudo": {"text": "# Regras de Teste"},
        "metadata": {
            "tema": "teste",
            "num_embates": 2,
            "data_criacao": datetime.now().isoformat(),
            "status": "ativo",
            "tipo_documento": "regra_condensada"
        },
        "embedding": [0.0] * 384  # Mock de embedding
    }

@pytest.fixture
def mock_embedding_response():
    """Mock de resposta do serviço de embeddings."""
    return [0.0] * 384  # Vetor de 384 dimensões com zeros

@pytest.fixture
def mock_health_response():
    """Mock de resposta do endpoint de health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0",
        "environment": "test"
    }

@pytest.fixture
def mock_settings(monkeypatch):
    """Mock das configurações."""
    test_settings = {
        "SUPABASE_URL": "http://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "LOCAL_URL": "http://localhost:10000",
        "ENVIRONMENT": "test"
    }
    
    for key, value in test_settings.items():
        monkeypatch.setenv(key, value)
    
    return test_settings

@pytest.fixture
def mock_supabase_client(mocker):
    """Mock do cliente Supabase."""
    mock_client = mocker.MagicMock()
    mock_client.rpc.return_value.execute.return_value = mock_supabase_response()
    return mock_client

@pytest.fixture
def mock_requests(mocker, mock_health_response):
    """Mock de requisições HTTP."""
    mock = mocker.patch("requests.get")
    mock.return_value.status_code = 200
    mock.return_value.json.return_value = mock_health_response
    return mock 