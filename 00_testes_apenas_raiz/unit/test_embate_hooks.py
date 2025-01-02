"""
Testes unitários para os hooks de embates.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_rag_ia.cli.embates.hooks import EmbateHooks
from backend_rag_ia.cli.embates.models import Embate

@pytest.fixture
def manager():
    """Fixture que cria um mock do manager."""
    return AsyncMock()

@pytest.fixture
def hooks(manager):
    """Fixture que cria hooks com manager mockado."""
    return EmbateHooks(manager=manager)

@pytest.fixture
def embate():
    """Fixture que cria um embate válido."""
    return Embate(
        titulo="Teste",
        tipo="TECNICO",
        contexto="Contexto de teste",
        status="aberto",
        data_inicio=datetime.now()
    )

async def test_pre_create_valido(hooks, embate):
    """Testa pre_create com embate válido."""
    await hooks.pre_create(embate)
    assert embate.tipo == "tecnico"
    assert "criado_em" in embate.metadata

async def test_pre_create_sem_titulo(hooks):
    """Testa pre_create sem título."""
    embate = Embate(
        titulo="",
        tipo="tecnico",
        contexto="Teste",
        status="aberto"
    )
    
    with pytest.raises(ValueError, match="Título é obrigatório"):
        await hooks.pre_create(embate)

async def test_pre_create_sem_contexto(hooks):
    """Testa pre_create sem contexto."""
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        contexto="",
        status="aberto"
    )
    
    with pytest.raises(ValueError, match="Contexto é obrigatório"):
        await hooks.pre_create(embate)

async def test_post_create(hooks, capsys):
    """Testa post_create."""
    embate = {"titulo": "Teste"}
    await hooks.post_create(embate)
    
    captured = capsys.readouterr()
    assert "Embate criado: Teste" in captured.out

async def test_pre_update_valido(hooks):
    """Testa pre_update com dados válidos."""
    updates = {
        "titulo": "Novo título",
        "tipo": "PREFERENCIA"
    }
    
    await hooks.pre_update("123", updates)
    assert updates["tipo"] == "preferencia"
    assert "atualizado_em" in updates["metadata"]

async def test_pre_update_titulo_vazio(hooks):
    """Testa pre_update com título vazio."""
    updates = {"titulo": ""}
    
    with pytest.raises(ValueError, match="Título não pode ser vazio"):
        await hooks.pre_update("123", updates)

async def test_pre_update_contexto_vazio(hooks):
    """Testa pre_update com contexto vazio."""
    updates = {"contexto": ""}
    
    with pytest.raises(ValueError, match="Contexto não pode ser vazio"):
        await hooks.pre_update("123", updates)

async def test_post_update(hooks, capsys):
    """Testa post_update."""
    embate = {
        "titulo": "Teste",
        "status": "resolvido"
    }
    
    await hooks.post_update(embate)
    
    captured = capsys.readouterr()
    assert "Embate atualizado: Teste" in captured.out
    assert "Embate resolvido: Teste" in captured.out

async def test_pre_search(hooks):
    """Testa pre_search."""
    query = "  TESTE  "
    result = await hooks.pre_search(query)
    assert result == "teste"

async def test_post_search(hooks):
    """Testa post_search."""
    results = [
        {"data_inicio": "2024-01-02"},
        {"data_inicio": "2024-01-03"},
        {"data_inicio": "2024-01-01"}
    ]
    
    processed = await hooks.post_search(results)
    assert processed[0]["data_inicio"] == "2024-01-03"
    assert processed[-1]["data_inicio"] == "2024-01-01"

async def test_pre_export(hooks):
    """Testa pre_export."""
    filters = {
        "tipo": "TECNICO",
        "status": "ABERTO"
    }
    
    processed = await hooks.pre_export(filters)
    assert processed["tipo"] == "tecnico"
    assert processed["status"] == "aberto"

async def test_post_export(hooks):
    """Testa post_export."""
    results = [
        {"titulo": "Teste 1"},
        {"titulo": "Teste 2"}
    ]
    
    processed = await hooks.post_export(results)
    assert all("exportado_em" in r["metadata"] for r in processed) 