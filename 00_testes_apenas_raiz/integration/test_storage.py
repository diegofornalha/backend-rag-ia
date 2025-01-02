"""Testes para o storage de embates."""

import pytest
from datetime import datetime
import subprocess
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
    
    # Primeira chamada
    embate1 = Embate(
        titulo="Teste 1",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste 1",
        data_inicio=datetime.now()
    )
    result1 = await storage.save(embate1)
    embates = await storage.list()
    assert len(embates) == 1
    
    # Segunda chamada
    embate2 = Embate(
        titulo="Teste 2",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste 2",
        data_inicio=datetime.now()
    )
    result2 = await storage.save(embate2)
    embates = await storage.list()
    assert len(embates) == 2
    
    # Terceira chamada - deve criar embate técnico e embate JSONB
    embate3 = Embate(
        titulo="Teste 3",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste 3",
        data_inicio=datetime.now()
    )
    result3 = await storage.save(embate3)
    embates = await storage.list()
    assert len(embates) == 6  # 3 embates originais + 1 embate técnico + 1 embate JSONB + 1 embate logs
    
    # Encontra o embate técnico
    embate_tecnico = next(e for e in embates if e.metadata.get("is_trigger_embate") and "Uso Intensivo" in e.titulo)
    assert embate_tecnico.tipo == "tecnico"
    assert "Uso Intensivo do Storage" in embate_tecnico.titulo
    
    # Encontra o embate JSONB
    embate_jsonb = next(e for e in embates if e.metadata.get("is_trigger_embate") and "JSONB" in e.titulo)
    assert embate_jsonb.tipo == "tecnico"
    assert "Migração para JSONB" in embate_jsonb.titulo
    assert len(embate_jsonb.argumentos) == 2
    assert "Análise Técnica" in embate_jsonb.argumentos[0]["conteudo"]
    assert "Impacto e Riscos" in embate_jsonb.argumentos[1]["conteudo"]
    
    # Encontra o embate de logs
    embate_logs = next(e for e in embates if e.metadata.get("is_trigger_embate") and "Logs" in e.titulo)
    assert embate_logs.tipo == "tecnico"
    assert "Padronização de Logs e Monitoramento" in embate_logs.titulo
    assert len(embate_logs.argumentos) == 2
    assert "Análise Técnica" in embate_logs.argumentos[0]["conteudo"]
    assert "Impacto e Riscos" in embate_logs.argumentos[1]["conteudo"]
    
    # Deleta os embates técnicos e verifica se o contador é resetado
    await storage.delete(embate_tecnico.id)
    await storage.delete(embate_jsonb.id)
    await storage.delete(embate_logs.id)
    embates = await storage.list()
    assert len(embates) == 3  # Apenas os embates originais
    
    # Faz mais uma chamada para verificar se não cria novos embates técnicos
    embate4 = Embate(
        titulo="Teste 4",
        tipo="tecnico",
        status="pendente",
        contexto="Contexto de teste 4",
        data_inicio=datetime.now()
    )
    result4 = await storage.save(embate4)
    embates = await storage.list()
    assert len(embates) == 4  # 4 embates originais 

@pytest.mark.asyncio
async def test_memory_storage_commit_push():
    """Testa o commit e push automático após ciclo de embates."""
    storage = MemoryStorage()
    
    # Mock das chamadas git
    with patch('subprocess.run') as mock_run:
        # Configura mock para simular alterações no git status
        mock_run.return_value.stdout = "M backend_rag_ia/cli/embates/storage/__init__.py"
        
        # Primeira chamada
        embate1 = Embate(
            titulo="Teste Commit 1",
            tipo="tecnico",
            status="pendente",
            contexto="Contexto de teste commit 1",
            data_inicio=datetime.now()
        )
        await storage.save(embate1)
        
        # Segunda chamada
        embate2 = Embate(
            titulo="Teste Commit 2",
            tipo="tecnico",
            status="pendente",
            contexto="Contexto de teste commit 2",
            data_inicio=datetime.now()
        )
        await storage.save(embate2)
        
        # Terceira chamada - deve criar embates técnicos e fazer commit
        embate3 = Embate(
            titulo="Teste Commit 3",
            tipo="tecnico",
            status="pendente",
            contexto="Contexto de teste commit 3",
            data_inicio=datetime.now()
        )
        await storage.save(embate3)
        
        # Verifica se git add, commit e push foram chamados
        git_calls = [call.args[0] for call in mock_run.call_args_list]
        assert ['git', 'status', '--porcelain'] in git_calls
        assert ['git', 'add', '.'] in git_calls
        assert any('git commit -m' in ' '.join(args) for args in git_calls)
        assert ['git', 'push'] in git_calls 