"""
Testes de integração para o sistema de embates.
"""

from pathlib import Path

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.tests.utils.test_helpers import (
    cleanup_test_files,
    create_test_embate,
)


@pytest.fixture
def test_dir():
    """Fixture que retorna um diretório temporário para testes."""
    path = Path("test_embates_integration")
    path.mkdir(exist_ok=True)
    yield path
    cleanup_test_files(path)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_search_embate():
    """Testa criação e busca de embate."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate(
        titulo="Teste de Integração",
        contexto="Teste de criação e busca"
    )
    
    # Act - Cria embate
    result = await manager.create_embate(embate)
    
    # Assert - Verifica criação
    assert result["status"] == "success"
    assert result["data"]["titulo"] == embate.titulo
    
    # Act - Busca embate
    results = await manager.search_embates("Integração")
    
    # Assert - Verifica busca
    assert len(results) == 1
    assert results[0]["titulo"] == embate.titulo

@pytest.mark.integration
@pytest.mark.asyncio
async def test_update_and_export_embate():
    """Testa atualização e exportação de embate."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate(
        titulo="Teste para Atualizar",
        status="aberto"
    )
    
    # Act - Cria embate
    result = await manager.create_embate(embate)
    embate_id = result["id"]
    
    # Act - Atualiza embate
    updates = {
        "status": "resolvido",
        "metadata": {
            "tags": ["atualizado"]
        }
    }
    update_result = await manager.update_embate(embate_id, updates)
    
    # Assert - Verifica atualização
    assert update_result["status"] == "success"
    assert update_result["data"]["status"] == "resolvido"
    
    # Act - Exporta embates
    export_results = await manager.export_embates({"status": "resolvido"})
    
    # Assert - Verifica exportação
    assert len(export_results) == 1
    assert export_results[0]["id"] == embate_id
    assert export_results[0]["status"] == "resolvido"

