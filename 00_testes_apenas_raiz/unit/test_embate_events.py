"""
Testes unitários para o sistema de eventos de embates.
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_rag_ia.cli.embates.events import EmbateEvent, EmbateEventManager

@pytest.fixture
def evento():
    """Fixture que cria um evento de teste."""
    return EmbateEvent(
        tipo="teste",
        dados={"mensagem": "Teste"},
        timestamp=datetime.now()
    )

@pytest.fixture
def manager():
    """Fixture que cria um gerenciador de eventos."""
    return EmbateEventManager()

def test_evento_init():
    """Testa inicialização de evento."""
    dados = {"mensagem": "Teste"}
    evento = EmbateEvent("teste", dados)
    
    assert evento.tipo == "teste"
    assert evento.dados == dados
    assert isinstance(evento.timestamp, datetime)

def test_evento_to_dict():
    """Testa conversão de evento para dicionário."""
    timestamp = datetime.now()
    dados = {"mensagem": "Teste"}
    evento = EmbateEvent("teste", dados, timestamp)
    
    result = evento.to_dict()
    assert result["tipo"] == "teste"
    assert result["dados"] == dados
    assert result["timestamp"] == timestamp.isoformat()

def test_manager_init():
    """Testa inicialização do gerenciador."""
    manager = EmbateEventManager()
    assert manager.handlers == {}
    assert manager.eventos == []

def test_register_handler(manager):
    """Testa registro de handler."""
    async def handler(evento): pass
    
    manager.register_handler("teste", handler)
    assert "teste" in manager.handlers
    assert handler in manager.handlers["teste"]

def test_unregister_handler(manager):
    """Testa remoção de handler."""
    async def handler(evento): pass
    
    manager.register_handler("teste", handler)
    manager.unregister_handler("teste", handler)
    assert "teste" not in manager.handlers

async def test_dispatch(manager):
    """Testa disparo de evento."""
    called = False
    
    async def handler(evento):
        nonlocal called
        called = True
        assert evento.tipo == "teste"
        
    manager.register_handler("teste", handler)
    await manager.dispatch(EmbateEvent("teste", {}))
    
    assert called
    assert len(manager.eventos) == 1

async def test_dispatch_error(manager, capsys):
    """Testa erro no disparo de evento."""
    async def handler(evento):
        raise ValueError("Erro de teste")
        
    manager.register_handler("teste", handler)
    await manager.dispatch(EmbateEvent("teste", {}))
    
    captured = capsys.readouterr()
    assert "Erro ao processar evento: Erro de teste" in captured.out

def test_get_eventos_tipo(manager, evento):
    """Testa filtragem de eventos por tipo."""
    outro_evento = EmbateEvent("outro", {})
    
    manager.eventos = [evento, outro_evento]
    eventos = manager.get_eventos(tipo="teste")
    
    assert len(eventos) == 1
    assert eventos[0].tipo == "teste"

def test_get_eventos_data(manager):
    """Testa filtragem de eventos por data."""
    agora = datetime.now()
    eventos = [
        EmbateEvent("teste", {}, agora - timedelta(days=2)),
        EmbateEvent("teste", {}, agora - timedelta(days=1)),
        EmbateEvent("teste", {}, agora)
    ]
    manager.eventos = eventos
    
    inicio = agora - timedelta(days=1)
    fim = agora
    
    filtrados = manager.get_eventos(inicio=inicio, fim=fim)
    assert len(filtrados) == 2

def test_clear_eventos(manager, evento):
    """Testa limpeza de eventos."""
    manager.eventos = [evento]
    manager.clear_eventos()
    assert manager.eventos == []

def test_export_eventos(manager, evento):
    """Testa exportação de eventos."""
    manager.eventos = [evento]
    exported = manager.export_eventos()
    
    assert len(exported) == 1
    assert exported[0]["tipo"] == evento.tipo
    assert exported[0]["dados"] == evento.dados
    assert exported[0]["timestamp"] == evento.timestamp.isoformat() 