"""
Testes unitários para o gerenciador de embates.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.cli.embates.models import Embate
from backend_rag_ia.cli.embates.storage import SupabaseStorage

@pytest.fixture
def storage():
    """Fixture que cria um mock do storage."""
    mock = AsyncMock(spec=SupabaseStorage)
    mock.save_embate = AsyncMock(return_value={"data": {"id": "123"}})
    mock.update_embate = AsyncMock(return_value={"data": {"id": "123"}})
    mock.search_embates = AsyncMock(return_value=[{"id": "123"}])
    mock.export_embates = AsyncMock(return_value=[{"id": "123"}])
    return mock

@pytest.fixture
def manager(storage):
    """Fixture que cria um gerenciador com storage mockado."""
    return EmbateManager(storage=storage)

@pytest.fixture
def embate():
    """Fixture que cria um embate válido."""
    return Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="Contexto de teste",
        status="aberto",
        data_inicio=datetime.now()
    )

async def test_create_embate_valido(manager, embate, storage):
    """Testa criação de embate válido."""
    result = await manager.create_embate(embate)
    assert result == {"data": {"id": "123"}}
    storage.save_embate.assert_called_once_with(embate)

async def test_create_embate_tipo_invalido(manager):
    """Testa erro ao criar embate com tipo inválido."""
    embate = Embate(
        titulo="Teste",
        tipo="invalido",
        contexto="Teste",
        status="aberto"
    )
    
    with pytest.raises(ValueError, match="Tipo de embate inválido"):
        await manager.create_embate(embate)

async def test_create_embate_status_invalido(manager):
    """Testa erro ao criar embate com status inválido."""
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="Teste",
        status="invalido"
    )
    
    with pytest.raises(ValueError, match="Status de embate inválido"):
        await manager.create_embate(embate)

async def test_update_embate_valido(manager, storage):
    """Testa atualização válida de embate."""
    updates = {"titulo": "Novo título"}
    result = await manager.update_embate("123", updates)
    assert result == {"data": {"id": "123"}}
    storage.update_embate.assert_called_once_with("123", updates)

async def test_update_embate_tipo_invalido(manager):
    """Testa erro ao atualizar embate com tipo inválido."""
    updates = {"tipo": "invalido"}
    
    with pytest.raises(ValueError, match="Tipo de embate inválido"):
        await manager.update_embate("123", updates)

async def test_update_embate_status_invalido(manager):
    """Testa erro ao atualizar embate com status inválido."""
    updates = {"status": "invalido"}
    
    with pytest.raises(ValueError, match="Status de embate inválido"):
        await manager.update_embate("123", updates)

async def test_update_embate_resolucao(manager, storage):
    """Testa atualização de embate com resolução."""
    updates = {"status": "resolvido"}
    await manager.update_embate("123", updates)
    
    call_args = storage.update_embate.call_args[0][1]
    assert "data_resolucao" in call_args
    assert isinstance(call_args["data_resolucao"], datetime)

async def test_search_embates(manager, storage):
    """Testa busca de embates."""
    result = await manager.search_embates("query")
    assert result == [{"id": "123"}]
    storage.search_embates.assert_called_once_with("query")

async def test_export_embates(manager, storage):
    """Testa exportação de embates."""
    filters = {"status": "aberto"}
    result = await manager.export_embates(filters)
    assert result == [{"id": "123"}]
    storage.export_embates.assert_called_once_with(filters)

async def test_get_embate_encontrado(manager, storage):
    """Testa busca de embate específico encontrado."""
    result = await manager.get_embate("123")
    assert result == {"id": "123"}
    storage.search_embates.assert_called_once_with("123")

async def test_get_embate_nao_encontrado(manager, storage):
    """Testa busca de embate específico não encontrado."""
    storage.search_embates.return_value = []
    result = await manager.get_embate("123")
    assert result is None 