"""
Testes de performance para o sistema de embates.
"""

import time

import pytest

from backend_rag_ia.cli.embates.manager import EmbateManager
from backend_rag_ia.tests.utils.test_helpers import create_test_embate


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_create_embate_performance():
    """Testa performance da criação de embates."""
    manager = EmbateManager()
    embate = create_test_embate()
    
    start_time = time.time()
    result = await manager.create_embate(embate)
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 1.0
    assert result["status"] == "success"


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_search_embates_performance():
    """Testa performance da busca de embates."""
    manager = EmbateManager()
    
    embates = [
        create_test_embate(
            titulo=f"Teste de Performance {i}",
            contexto=f"Contexto para teste de performance {i}"
        )
        for i in range(10)
    ]
    
    for embate in embates:
        await manager.create_embate(embate)
    
    start_time = time.time()
    results = await manager.search_embates("performance")
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 2.0
    assert len(results) > 0


@pytest.mark.monitoring
@pytest.mark.asyncio
async def test_update_embate_performance():
    """Testa performance da atualização de embates."""
    manager = EmbateManager()
    embate = create_test_embate()
    result = await manager.create_embate(embate)
    embate_id = result["id"]
    
    updates = {
        "titulo": "Teste Atualizado",
        "status": "resolvido"
    }
    
    start_time = time.time()
    result = await manager.update_embate(embate_id, updates)
    end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 1.0
    assert result["status"] == "success" 