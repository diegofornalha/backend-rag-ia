"""Fixtures compartilhadas para testes."""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest


# Fixtures para dados de exemplo
@pytest.fixture
def sample_embate_data():
    """Retorna dados de exemplo para um embate."""
    return {
        "titulo": "Embate Teste",
        "tipo": "tecnico",
        "contexto": "Contexto de teste",
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [
            {
                "autor": "AI",
                "tipo": "tecnico",
                "conteudo": "Argumento de teste",
                "data": datetime.now().isoformat()
            }
        ],
        "decisao": None,
        "razao": None,
        "arquivo": "embate_test.json"
    }

@pytest.fixture
def sample_rules_data():
    """Retorna dados de exemplo para regras."""
    return {
        "titulo": "Regras Teste",
        "tema": "Testes",
        "contexto": "Contexto das regras",
        "decisoes": [
            {
                "titulo": "Decisão 1",
                "conteudo": "Conteúdo da decisão 1",
                "razao": "Razão da decisão 1"
            }
        ],
        "metadados": {
            "data_criacao": datetime.now().isoformat(),
            "num_embates": 1,
            "arquivos_origem": ["embate_test.json"]
        }
    }

# Fixtures para mocks
@pytest.fixture
def mock_supabase_response():
    """Mock de resposta do Supabase."""
    return {
        "data": {
            "id": 1,
            "created_at": datetime.now().isoformat(),
            "status": "success"
        }
    }

@pytest.fixture
def mock_embedding_response():
    """Mock de resposta de embedding."""
    return [0.1, 0.2, 0.3, 0.4, 0.5]

@pytest.fixture
def mock_health_response():
    """Mock de resposta do health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": 3600,
        "metrics": {
            "documents": 100,
            "embeddings": 100
        }
    }

# Fixtures para diretórios temporários
@pytest.fixture
def temp_test_dir(tmp_path):
    """Cria estrutura de diretórios temporários para testes."""
    # Diretórios principais
    embates_dir = tmp_path / "embates"
    regras_dir = tmp_path / "regras"
    cache_dir = tmp_path / "cache"
    
    # Subdiretórios
    embates_dir.mkdir()
    regras_dir.mkdir()
    cache_dir.mkdir()
    
    (regras_dir / "frontend").mkdir()
    (regras_dir / "backend").mkdir()
    (cache_dir / "embeddings").mkdir()
    
    return {
        "root": tmp_path,
        "embates": embates_dir,
        "regras": regras_dir,
        "cache": cache_dir
    }

@pytest.fixture
def temp_embate_file(temp_test_dir, sample_embate_data):
    """Cria um arquivo de embate temporário."""
    file_path = temp_test_dir["embates"] / "embate_test.json"
    with open(file_path, "w") as f:
        json.dump(sample_embate_data, f)
    return file_path

@pytest.fixture
def temp_rules_file(temp_test_dir, sample_rules_data):
    """Cria um arquivo de regras temporário."""
    file_path = temp_test_dir["regras"] / "frontend" / "regras_test.md"
    with open(file_path, "w") as f:
        json.dump(sample_rules_data, f)
    return file_path

# Fixtures para mocks de serviços
@pytest.fixture
def mock_supabase_client():
    """Mock do cliente Supabase."""
    client = MagicMock()
    client.rpc.return_value.execute.return_value = {"data": {"id": 1}}
    return client

@pytest.fixture
def mock_semantic_search():
    """Mock do serviço de busca semântica."""
    service = MagicMock()
    service.search.return_value = {
        "results": [
            {
                "id": 1,
                "content": "Conteúdo teste",
                "similarity": 0.9
            }
        ]
    }
    return service

@pytest.fixture
def mock_logger():
    """Mock do logger."""
    logger = MagicMock()
    return logger

# Fixtures para configurações
@pytest.fixture
def test_settings():
    """Configurações para teste."""
    return {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_KEY": "test-key",
        "ENVIRONMENT": "test",
        "DEBUG": True,
        "LOCAL_URL": "http://localhost:10000"
    }

# Fixtures para utilidades
@pytest.fixture
def sample_markdown():
    """Retorna um exemplo de conteúdo markdown."""
    return """# Título

## Seção 1
Conteúdo da seção 1

## Seção 2
Conteúdo da seção 2

### Subseção 2.1
- Item 1
- Item 2

## Metadados
- Data: 2024-01-01
- Autor: Test
"""

@pytest.fixture
def sample_json():
    """Retorna um exemplo de conteúdo JSON."""
    return {
        "title": "Test",
        "sections": [
            {
                "name": "Section 1",
                "content": "Content 1"
            },
            {
                "name": "Section 2",
                "content": "Content 2",
                "subsections": [
                    {
                        "name": "Subsection 2.1",
                        "items": ["Item 1", "Item 2"]
                    }
                ]
            }
        ],
        "metadata": {
            "date": "2024-01-01",
            "author": "Test"
        }
    } 