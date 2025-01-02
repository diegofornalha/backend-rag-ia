"""
Testes unitários para storage de embates.
"""

import pytest
from datetime import datetime
from backend_rag_ia.cli.embates.storage import SupabaseStorage
from backend_rag_ia.cli.embates.models import Embate, Argumento
from ..5_utils.test_helpers import MockSupabaseClient

@pytest.fixture
def mock_supabase_client():
    """Fixture que retorna um cliente Supabase mockado."""
    return MockSupabaseClient({
        "save_embate_with_embedding": {
            "id": "123",
            "status": "success",
            "data": {
                "titulo": "Teste",
                "tipo": "tecnico",
                "status": "aberto"
            }
        },
        "update_embate": {
            "id": "123",
            "status": "success",
            "data": {
                "titulo": "Teste Atualizado",
                "tipo": "tecnico",
                "status": "resolvido"
            }
        },
        "search_embates": [
            {
                "id": "123",
                "titulo": "Teste",
                "tipo": "tecnico",
                "status": "aberto"
            }
        ],
        "export_embates": [
            {
                "id": "123",
                "titulo": "Teste",
                "tipo": "tecnico",
                "status": "aberto"
            }
        ]
    })

@pytest.fixture
def storage(mock_supabase_client, monkeypatch):
    """Fixture que retorna uma instância de SupabaseStorage com cliente mockado."""
    def mock_create_client(*args, **kwargs):
        return mock_supabase_client
    
    monkeypatch.setattr("backend_rag_ia.cli.embates.storage.create_client", mock_create_client)
    return SupabaseStorage()

@pytest.mark.asyncio
async def test_save_embate(storage):
    """Testa salvamento de embate."""
    # Arrange
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="Contexto de teste",
        status="aberto",
        data_inicio=datetime.now(),
        argumentos=[
            Argumento(
                autor="Testador",
                conteudo="Argumento de teste",
                tipo="tecnico",
                data=datetime.now()
            )
        ],
        arquivo="teste.json"
    )
    
    # Act
    result = await storage.save_embate(embate)
    
    # Assert
    assert result["id"] == "123"
    assert result["status"] == "success"
    assert result["data"]["titulo"] == "Teste"
    assert result["data"]["tipo"] == "tecnico"
    assert result["data"]["status"] == "aberto"

@pytest.mark.asyncio
async def test_update_embate(storage):
    """Testa atualização de embate."""
    # Arrange
    embate_id = "123"
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    # Act
    result = await storage.update_embate(embate_id, updates)
    
    # Assert
    assert result["id"] == "123"
    assert result["status"] == "success"
    assert result["data"]["titulo"] == "Teste Atualizado"
    assert result["data"]["status"] == "resolvido"

@pytest.mark.asyncio
async def test_search_embates(storage):
    """Testa busca de embates."""
    # Arrange
    query = "teste"
    
    # Act
    results = await storage.search_embates(query)
    
    # Assert
    assert len(results) == 1
    assert results[0]["id"] == "123"
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto"

@pytest.mark.asyncio
async def test_export_embates(storage):
    """Testa exportação de embates."""
    # Arrange
    filters = {"status": "aberto"}
    
    # Act
    results = await storage.export_embates(filters)
    
    # Assert
    assert len(results) == 1
    assert results[0]["id"] == "123"
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto" 