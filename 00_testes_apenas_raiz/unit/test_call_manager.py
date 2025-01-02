"""
Testes unitários para o gerenciador de chamadas sequenciais.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from backend_rag_ia.services.call_manager import ChamadasSequenciaisManager

@pytest.fixture
def manager():
    """Fixture que cria um gerenciador com configuração de teste."""
    return ChamadasSequenciaisManager(
        limite_aviso=3,
        limite_maximo=5,
        tempo_reset=1,
        arquivo_estado="test_chamadas.json"
    )

@pytest.fixture(autouse=True)
def cleanup():
    """Fixture que limpa arquivos de teste."""
    yield
    Path("test_chamadas.json").unlink(missing_ok=True)

def test_init():
    """Testa inicialização do gerenciador."""
    manager = ChamadasSequenciaisManager()
    assert manager.limite_aviso == 15
    assert manager.limite_maximo == 25
    assert manager.tempo_reset == 60
    assert manager.chamadas == []

def test_registrar_chamada_sucesso(manager):
    """Testa registro de chamada com sucesso."""
    result = manager.registrar_chamada("test")
    assert result["status"] == "success"
    assert len(manager.chamadas) == 1
    assert manager.chamadas[0].tipo == "test"

def test_registrar_chamada_warning(manager):
    """Testa aviso ao atingir limite de aviso."""
    for i in range(3):
        manager.registrar_chamada("test")
        
    result = manager.registrar_chamada("test")
    assert result["status"] == "warning"
    assert "sugestoes" in result
    assert len(result["sugestoes"]) > 0
    assert "Considere pausar para revisão" in result["message"]

def test_registrar_chamada_erro(manager):
    """Testa erro ao atingir limite máximo."""
    for i in range(5):
        manager.registrar_chamada("test")
        
    result = manager.registrar_chamada("test")
    assert result["status"] == "error"
    assert "Limite de 5 chamadas atingido" in result["message"]

def test_reset_por_tempo(manager):
    """Testa reset automático por tempo."""
    manager.registrar_chamada("test")
    
    # Simula passagem de tempo
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime.now() + timedelta(minutes=2)
        result = manager.registrar_chamada("test")
        
    assert result["status"] == "success"
    assert len(manager.chamadas) == 1

def test_persistencia(manager):
    """Testa persistência do estado."""
    manager.registrar_chamada("test", "contexto")
    
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

def test_sugestoes(manager):
    """Testa geração de sugestões."""
    # Registra várias chamadas do mesmo tipo
    for i in range(6):
        manager.registrar_chamada("repetido")
        
    result = manager.registrar_chamada("outro")
    assert "sugestoes" in result
    assert any("repetido" in s for s in result["sugestoes"])
    assert "Revise o progresso atual" in result["sugestoes"] 