"""
Testes unitários para o gerenciador de chamadas sequenciais.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend_rag_ia.services.call_manager import ChamadasSequenciaisManager


@pytest.fixture
def arquivo_temp(tmp_path):
    """Fixture que retorna um arquivo temporário."""
    return tmp_path / "estado_teste.json"

@pytest.fixture
def manager(arquivo_temp):
    """Fixture que retorna uma instância do gerenciador."""
    return ChamadasSequenciaisManager(
        limite_aviso=5,
        limite_maximo=8,
        arquivo_estado=str(arquivo_temp)
    )

def test_inicializacao(manager):
    """Testa inicialização do gerenciador."""
    assert manager.contador == 0
    assert manager.limite_aviso == 5
    assert manager.limite_maximo == 8
    assert manager.ultima_chamada is None

def test_registro_chamada_simples(manager):
    """Testa registro de chamada simples."""
    resultado = manager.registrar_chamada()
    assert resultado is None
    assert manager.contador == 1
    assert manager.ultima_chamada is not None

def test_aviso_limite(manager):
    """Testa geração de aviso ao atingir limite."""
    # Registra chamadas até limite de aviso
    for _ in range(4):
        assert manager.registrar_chamada() is None
    
    # Verifica aviso na próxima chamada
    resultado = manager.registrar_chamada()
    assert resultado is not None
    assert resultado["tipo"] == "sistema"
    assert "Limite de Chamadas Sequenciais" in resultado["titulo"]
    assert manager.contador == 5

def test_reset_por_tempo(manager, monkeypatch):
    """Testa reset do contador por tempo de inatividade."""
    # Primeira chamada
    manager.registrar_chamada()
    assert manager.contador == 1
    
    # Simula passagem de tempo
    ultima_chamada = datetime.now() - timedelta(minutes=2)
    manager.ultima_chamada = ultima_chamada
    
    # Nova chamada deve resetar contador
    manager.registrar_chamada()
    assert manager.contador == 1

def test_persistencia_estado(manager, arquivo_temp):
    """Testa persistência do estado em arquivo."""
    # Registra algumas chamadas
    manager.registrar_chamada()
    manager.registrar_chamada()
    
    # Verifica arquivo de estado
    assert arquivo_temp.exists()
    estado = json.loads(arquivo_temp.read_text())
    assert estado["contador"] == 2
    assert estado["ultima_chamada"] is not None
    
    # Cria novo gerenciador com mesmo arquivo
    novo_manager = ChamadasSequenciaisManager(
        limite_aviso=5,
        limite_maximo=8,
        arquivo_estado=str(arquivo_temp)
    )
    
    # Verifica se estado foi carregado
    assert novo_manager.contador == 2
    assert novo_manager.ultima_chamada is not None

def test_reset_manual(manager):
    """Testa reset manual do contador."""
    # Registra algumas chamadas
    manager.registrar_chamada()
    manager.registrar_chamada()
    assert manager.contador == 2
    
    # Reseta manualmente
    manager.resetar()
    assert manager.contador == 0
    assert manager.ultima_chamada is None

def test_sugestoes_embate(manager):
    """Testa sugestões no embate de aviso."""
    # Registra chamadas até limite
    for _ in range(5):
        resultado = manager.registrar_chamada()
    
    # Verifica sugestões
    assert "sugestoes" in resultado
    sugestoes = resultado["sugestoes"]
    assert "pausar" in sugestoes
    assert "continuar" in sugestoes
    assert "salvar" in sugestoes
    assert "reiniciar" in sugestoes

def test_erro_arquivo_estado(arquivo_temp):
    """Testa recuperação de erro no arquivo de estado."""
    # Cria arquivo com conteúdo inválido
    arquivo_temp.write_text("conteúdo inválido")
    
    # Gerenciador deve iniciar com estado padrão
    manager = ChamadasSequenciaisManager(arquivo_estado=str(arquivo_temp))
    assert manager.contador == 0
    assert manager.ultima_chamada is None 