"""
Testes unitários para o gerenciador de chamadas sequenciais.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from backend_rag_ia.services.call_manager import ChamadasSequenciaisManager
from backend_rag_ia.cli.embates.manager import EmbateManager

@pytest.fixture
def embate_manager():
    """Fixture que cria um mock do EmbateManager."""
    manager = AsyncMock(spec=EmbateManager)
    manager.create_embate = AsyncMock(return_value={"data": {"id": "123"}})
    return manager

@pytest.fixture
def manager(embate_manager):
    """Fixture que cria um gerenciador com configuração de teste."""
    manager = ChamadasSequenciaisManager(
        limite_retomada=3,
        limite_maximo=5,
        tempo_reset=1,
        arquivo_estado="test_chamadas.json"
    )
    manager.embate_manager = embate_manager
    return manager

@pytest.fixture(autouse=True)
def cleanup():
    """Fixture que limpa arquivos de teste."""
    yield
    Path("test_chamadas.json").unlink(missing_ok=True)

def test_init():
    """Testa inicialização do gerenciador."""
    manager = ChamadasSequenciaisManager()
    assert manager.limite_retomada == 15
    assert manager.limite_maximo == 25
    assert manager.tempo_reset == 60
    assert manager.chamadas == []

async def test_registrar_chamada_sucesso(manager):
    """Testa registro de chamada com sucesso."""
    result = await manager.registrar_chamada("test")
    assert result["status"] == "success"
    assert len(manager.chamadas) == 1
    assert manager.chamadas[0].tipo == "test"

async def test_registrar_chamada_retomada(manager, embate_manager):
    """Testa retomada ao atingir limite."""
    for i in range(3):
        await manager.registrar_chamada("test")
        
    result = await manager.registrar_chamada("test")
    assert result["status"] == "retomada"
    assert "Contamos 4 chamadas" in result["message"]
    assert result["chamadas_restantes"] == 1
    assert embate_manager.create_embate.called

async def test_registrar_chamada_erro(manager):
    """Testa erro ao atingir limite máximo."""
    for i in range(5):
        await manager.registrar_chamada("test")
        
    result = await manager.registrar_chamada("test")
    assert result["status"] == "error"
    assert "Limite de 5 chamadas atingido" in result["message"]

async def test_reset_por_tempo(manager):
    """Testa reset automático por tempo."""
    await manager.registrar_chamada("test")
    
    # Simula passagem de tempo
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime.now() + timedelta(minutes=2)
        result = await manager.registrar_chamada("test")
        
    assert result["status"] == "success"
    assert len(manager.chamadas) == 1

async def test_persistencia(manager):
    """Testa persistência do estado."""
    await manager.registrar_chamada("test", "contexto")
    
    # Verifica arquivo
    assert Path("test_chamadas.json").exists()
    data = json.loads(Path("test_chamadas.json").read_text())
    assert len(data["chamadas"]) == 1
    assert data["chamadas"][0]["tipo"] == "test"
    assert data["chamadas"][0]["contexto"] == "contexto"
    
    # Carrega novo gerenciador
    new_manager = ChamadasSequenciaisManager(
        arquivo_estado="test_chamadas.json"
    )
    assert len(new_manager.chamadas) == 1
    assert new_manager.chamadas[0].tipo == "test"
    assert new_manager.chamadas[0].contexto == "contexto"

async def test_criar_embate_retomada(manager, embate_manager):
    """Testa criação de embate de retomada."""
    # Registra chamadas até o limite
    for i in range(3):
        await manager.registrar_chamada("test")
    await manager.registrar_chamada("outro")
    
    # Verifica chamada ao create_embate
    call_args = embate_manager.create_embate.call_args[0][0]
    assert "Retomada de Execução" in call_args.titulo
    assert call_args.tipo == "sistema"
    assert "Atingido 4 chamadas" in call_args.contexto
    assert "chamadas_registradas" in call_args.metadata
    assert "tipos_chamada" in call_args.metadata 