"""
Testes de performance para o sistema de embates.
"""

import asyncio
import time

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.tests.utils.test_helpers import create_test_embate


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_create_embate_performance():
    """Testa performance da criação de embates."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate()
    
    # Act
    start_time = time.time()
    result = await manager.create_embate(embate)
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.0  # Deve levar menos de 1 segundo
    assert result["status"] == "success"


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_search_embates_performance():
    """Testa performance da busca de embates."""
    # Arrange
    manager = EmbateManager()
    
    # Cria alguns embates para buscar
    embates = [
        create_test_embate(
            titulo=f"Teste de Performance {i}",
            contexto=f"Contexto para teste de performance {i}"
        )
        for i in range(10)
    ]
    
    for embate in embates:
        await manager.create_embate(embate)
    
    # Act
    start_time = time.time()
    results = await manager.search_embates("performance")
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 2.0  # Deve levar menos de 2 segundos
    assert len(results) > 0


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_update_embate_performance():
    """Testa performance da atualização de embates."""
    # Arrange
    manager = EmbateManager()
    embate = create_test_embate()
    result = await manager.create_embate(embate)
    embate_id = result["id"]
    
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    # Act
    start_time = time.time()
    result = await manager.update_embate(embate_id, updates)
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.0  # Deve levar menos de 1 segundo
    assert result["status"] == "success"


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_export_embates_performance():
    """Testa performance da exportação de embates."""
    # Arrange
    manager = EmbateManager()
    
    # Cria alguns embates para exportar
    embates = [
        create_test_embate(
            titulo=f"Teste para Exportação {i}",
            status="aberto"
        )
        for i in range(5)
    ]
    
    for embate in embates:
        await manager.create_embate(embate)
    
    # Act
    start_time = time.time()
    results = await manager.export_embates({"status": "aberto"})
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 1.5  # Deve levar menos de 1.5 segundos
    assert len(results) >= 5


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_concurrent_operations_performance():
    """Testa performance de operações concorrentes."""
    # Arrange
    manager = EmbateManager()
    embates = [
        create_test_embate(
            titulo=f"Teste Concorrente {i}",
            contexto=f"Contexto para teste concorrente {i}"
        )
        for i in range(3)
    ]
    
    # Act
    start_time = time.time()
    
    # Executa operações concorrentemente
    create_tasks = [manager.create_embate(embate) for embate in embates]
    search_task = manager.search_embates("concorrente")
    export_task = manager.export_embates({"status": "aberto"})
    
    # Aguarda todas as operações
    results = await asyncio.gather(
        *create_tasks,
        search_task,
        export_task
    )
    
    end_time = time.time()
    
    # Assert
    duration = end_time - start_time
    assert duration < 3.0  # Deve levar menos de 3 segundos
    
    # Verifica resultados
    create_results = results[:3]
    search_results = results[3]
    export_results = results[4]
    
    assert all(r["status"] == "success" for r in create_results)
    assert len(search_results) > 0
    assert len(export_results) > 0 