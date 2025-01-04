"""Testes para o storage de embates."""

import pytest
from datetime import datetime
from unittest.mock import patch

from backend_rag_ia.cli.embates.models import Embate
from backend_rag_ia.cli.embates.storage import MemoryStorage

@pytest.mark.asyncio
async def test_memory_storage():
    """Testa o storage em memória."""
    storage = MemoryStorage()
    
    # Testa salvar
    embate = Embate(
        titulo="Teste",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste",
        data_inicio=datetime.now()
    )
    
    result = await storage.save(embate)
    assert "data" in result
    assert "id" in result["data"]
    assert result["data"]["id"].startswith("local-")
    
    # Testa buscar
    saved_embate = await storage.get(result["data"]["id"])
    assert saved_embate is not None
    assert saved_embate.titulo == "Teste"
    assert saved_embate.contexto == "Contexto de teste"
    
    # Testa listar
    embates = await storage.list()
    assert len(embates) == 1
    assert embates[0].id == result["data"]["id"]
    
    # Testa deletar
    await storage.delete(result["data"]["id"])
    assert await storage.get(result["data"]["id"]) is None
    embates = await storage.list()
    assert len(embates) == 0

@pytest.mark.asyncio
async def test_memory_storage_embate_trigger():
    """Testa a criação automática de embate após 3 chamadas."""
    storage = MemoryStorage()
    
    # Cria 3 embates em sequência
    for i in range(3):
        embate = Embate(
            titulo=f"Teste {i+1}",
            tipo="tecnico",
            status="pendente",
            contexto=f"Contexto de teste {i+1}",
            data_inicio=datetime.now()
        )
        await storage.save(embate)
        embates = await storage.list()
        assert len(embates) == i + 1
    
    # Verifica se foram criados os embates técnicos
    embates = await storage.list()
    assert len(embates) > 3  # Deve ter mais que os 3 embates originais
    
    # Verifica embates técnicos principais
    embate_tecnico = next(e for e in embates if e.metadata.get("is_trigger_embate") and "Storage" in e.titulo)
    assert embate_tecnico.tipo == "tecnico"
    assert len(embate_tecnico.argumentos) == 2
    assert "Análise Técnica" in embate_tecnico.argumentos[0]["conteudo"]
    assert "Impacto e Riscos" in embate_tecnico.argumentos[1]["conteudo"]
    
    # Limpa os embates técnicos
    for embate in embates:
        if embate.metadata.get("is_trigger_embate"):
            await storage.delete(embate.id)
    
    # Verifica se voltou ao estado original
    embates = await storage.list()
    assert len(embates) == 3  # Apenas os embates originais
    
    # Verifica se não cria novos embates técnicos
    embate4 = Embate(
        titulo="Teste 4",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste 4",
        data_inicio=datetime.now()
    )
    await storage.save(embate4)
    embates = await storage.list()
    assert len(embates) == 4  # 4 embates originais 