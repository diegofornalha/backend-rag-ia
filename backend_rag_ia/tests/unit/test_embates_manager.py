"""
Testes unitários para manager de embates.
"""

from pathlib import Path

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.cli.embates.storage import SupabaseStorage
from backend_rag_ia.tests.utils.test_helpers import (
    MockSupabaseClient,
    cleanup_test_files,
    create_test_embate,
    create_test_file,
)


@pytest.fixture
def test_dir():
    """Fixture que retorna um diretório temporário para testes."""
    path = Path("test_embates")
    path.mkdir(exist_ok=True)
    yield path
    cleanup_test_files(path)


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
        }
    })


@pytest.fixture
def storage(mock_supabase_client, monkeypatch):
    """Fixture que retorna uma instância de SupabaseStorage com cliente mockado."""
    def mock_create_client(*args, **kwargs):
        return mock_supabase_client
    
    monkeypatch.setattr("backend_rag_ia.cli.embates.storage.create_client", mock_create_client)
    return SupabaseStorage()


@pytest.fixture
def manager(storage):
    """Fixture que retorna uma instância do EmbateManager para testes."""
    return EmbateManager(storage=storage)


@pytest.mark.asyncio
async def test_create_embate_without_conflicts(manager):
    """Testa criação de embate sem conflitos."""
    embate = create_test_embate()
    result = await manager.create_embate(embate)
    
    assert result["status"] == "success"
    assert result["data"]["titulo"] == embate.titulo
    assert result["data"]["tipo"] == embate.tipo
    assert result["data"]["status"] == "aberto"


@pytest.mark.asyncio
async def test_create_embate_with_conflicts(manager, test_dir):
    """Testa criação de embate com conflitos."""
    embate = create_test_embate()
    create_test_file(embate, test_dir)
    
    manager.conflict_resolver.known_locations = [str(test_dir)]
    
    result = await manager.create_embate(embate)
    
    assert result["status"] == "success"
    assert result["data"]["titulo"] == embate.titulo
    assert not (test_dir / embate.arquivo).exists()
    assert (test_dir / "backup").exists()


@pytest.mark.asyncio
async def test_update_embate(manager):
    """Testa atualização de embate."""
    embate_id = "123"
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    result = await manager.update_embate(embate_id, updates)
    
    assert result["status"] == "success"
    assert result["data"]["titulo"] == updates["titulo"]
    assert result["data"]["status"] == updates["status"]


@pytest.mark.asyncio
async def test_search_embates(manager):
    """Testa busca de embates."""
    query = "teste"
    
    results = await manager.search_embates(query)
    
    assert len(results) == 1
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto"


@pytest.mark.asyncio
async def test_export_embates(manager):
    """Testa exportação de embates."""
    filters = {"status": "aberto"}
    
    results = await manager.export_embates(filters)
    
    assert len(results) == 1
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto" 