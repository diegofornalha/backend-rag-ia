"""
Testes de integração para o sistema de embates.
"""

import pytest
from pathlib import Path
import json
from datetime import datetime
from backend_rag_ia.cli.embates.models import Embate, Argumento
from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.cli.embates.storage import SupabaseStorage
from ..5_utils.test_helpers import (
    create_test_embate,
    create_test_file,
    cleanup_test_files
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

@pytest.mark.integration
@pytest.mark.asyncio
async def test_conflict_resolution_flow(test_dir):
    """Testa fluxo completo de resolução de conflitos."""
    # Arrange
    manager = EmbateManager()
    manager.conflict_resolver.known_locations = [str(test_dir)]
    
    # Cria embate original
    original_embate = create_test_embate(
        titulo="Embate Conflitante",
        version_key="conflito_v1"
    )
    create_test_file(original_embate, test_dir)
    
    # Cria novo embate com mesmo version_key
    new_embate = create_test_embate(
        titulo="Embate Conflitante Atualizado",
        version_key="conflito_v1"
    )
    
    # Act
    result = await manager.create_embate(new_embate)
    
    # Assert
    assert result["status"] == "success"
    assert result["data"]["titulo"] == new_embate.titulo
    assert not (test_dir / original_embate.arquivo).exists()
    assert (test_dir / "backup").exists()

@pytest.mark.integration
@pytest.mark.asyncio
async def test_semantic_search_flow():
    """Testa fluxo de busca semântica."""
    # Arrange
    manager = EmbateManager()
    
    # Cria embates com contextos relacionados
    embates = [
        create_test_embate(
            titulo="Arquitetura de Software",
            contexto="Decisões sobre padrões de projeto e estrutura do código"
        ),
        create_test_embate(
            titulo="Design Patterns",
            contexto="Implementação de padrões de projeto no sistema"
        ),
        create_test_embate(
            titulo="Tema Não Relacionado",
            contexto="Assunto completamente diferente"
        )
    ]
    
    # Act - Cria embates
    for embate in embates:
        await manager.create_embate(embate)
    
    # Act - Busca por similaridade
    results = await manager.search_embates("padrões de desenvolvimento de software")
    
    # Assert
    assert len(results) >= 2  # Deve encontrar pelo menos os dois primeiros
    titles = [r["titulo"] for r in results]
    assert "Arquitetura de Software" in titles
    assert "Design Patterns" in titles

@pytest.mark.integration
@pytest.mark.asyncio
async def test_metadata_handling():
    """Testa manipulação de metadados."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate(
        titulo="Teste de Metadados",
        metadata={
            "tags": ["teste", "metadata"],
            "prioridade": "alta",
            "categoria": "tecnico"
        }
    )
    
    # Act - Cria embate
    result = await manager.create_embate(embate)
    embate_id = result["id"]
    
    # Act - Atualiza metadados
    updates = {
        "metadata": {
            "tags": ["teste", "metadata", "atualizado"],
            "prioridade": "baixa"
        }
    }
    update_result = await manager.update_embate(embate_id, updates)
    
    # Assert
    assert update_result["status"] == "success"
    assert "atualizado" in update_result["data"]["metadata"]["tags"]
    assert update_result["data"]["metadata"]["prioridade"] == "baixa"
    assert update_result["data"]["metadata"]["categoria"] == "tecnico" 