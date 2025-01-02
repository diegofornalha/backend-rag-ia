"""
Testes unitários para manager de embates.
"""

from pathlib import Path

import pytest

from backend_rag_ia.cli.embates.manager import ConflictResolver, EmbateManager
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
    """Fixture que retorna uma instância de EmbateManager."""
    return EmbateManager(storage=storage)

@pytest.mark.asyncio
async def test_create_embate_without_conflicts(manager):
    """Testa criação de embate sem conflitos."""
    # Arrange
    embate = create_test_embate()
    
    # Act
    result = await manager.create_embate(embate)
    
    # Assert
    assert result["status"] == "success"
    assert result["data"]["titulo"] == embate.titulo
    assert result["data"]["tipo"] == embate.tipo
    assert result["data"]["status"] == embate.status

@pytest.mark.asyncio
async def test_create_embate_with_conflicts(manager, test_dir):
    """Testa criação de embate com conflitos."""
    # Arrange
    embate = create_test_embate()
    create_test_file(embate, test_dir)
    
    # Configura known_locations do ConflictResolver
    manager.conflict_resolver.known_locations = [str(test_dir)]
    
    # Act
    result = await manager.create_embate(embate)
    
    # Assert
    assert result["status"] == "success"
    assert result["data"]["titulo"] == embate.titulo
    assert not (test_dir / embate.arquivo).exists()
    assert (test_dir / "backup").exists()

@pytest.mark.asyncio
async def test_update_embate(manager):
    """Testa atualização de embate."""
    # Arrange
    embate_id = "123"
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    # Act
    result = await manager.update_embate(embate_id, updates)
    
    # Assert
    assert result["status"] == "success"
    assert result["data"]["titulo"] == updates["titulo"]
    assert result["data"]["status"] == updates["status"]

@pytest.mark.asyncio
async def test_search_embates(manager):
    """Testa busca de embates."""
    # Arrange
    query = "teste"
    
    # Act
    results = await manager.search_embates(query)
    
    # Assert
    assert len(results) == 1
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto"

@pytest.mark.asyncio
async def test_export_embates(manager):
    """Testa exportação de embates."""
    # Arrange
    filters = {"status": "aberto"}
    
    # Act
    results = await manager.export_embates(filters)
    
    # Assert
    assert len(results) == 1
    assert results[0]["titulo"] == "Teste"
    assert results[0]["tipo"] == "tecnico"
    assert results[0]["status"] == "aberto"

def test_conflict_resolver_has_conflicts(test_dir):
    """Testa detecção de conflitos."""
    # Arrange
    resolver = ConflictResolver()
    resolver.known_locations = [str(test_dir)]
    
    embate = create_test_embate()
    create_test_file(embate, test_dir)
    
    # Act
    has_conflicts = resolver.has_conflicts(embate)
    
    # Assert
    assert has_conflicts

@pytest.mark.asyncio
async def test_conflict_resolver_resolve_conflicts(test_dir):
    """Testa resolução de conflitos."""
    # Arrange
    resolver = ConflictResolver()
    resolver.known_locations = [str(test_dir)]
    
    embate = create_test_embate()
    create_test_file(embate, test_dir)
    
    # Act
    await resolver.resolve_conflicts(embate)
    
    # Assert
    assert not (test_dir / embate.arquivo).exists()
    assert (test_dir / "backup").exists() 