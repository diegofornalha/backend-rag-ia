"""
Testes para o gerenciador de chamadas sequenciais.
"""

import os
import tempfile
from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock
import json

from ..utils.sequential_calls import ChamadasSequenciaisManager, SequentialCallsConfig

@pytest.fixture
def temp_storage():
    """Fixture que cria arquivo temporário para storage."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def custom_config():
    """Fixture que cria configuração customizada."""
    return SequentialCallsConfig(
        LIMITE_AVISO=15,
        LIMITE_MAXIMO=20,
        TEMPO_RESET=60,
        NIVEIS_ALERTA=[5, 10, 15, 18],
        BACKUP_ENABLED=True,
        MAX_BACKUP_FILES=3
    )

def test_init_default():
    """Testa inicialização com valores default."""
    manager = ChamadasSequenciaisManager()
    assert manager.contador == 0
    assert manager.config.LIMITE_AVISO == 20
    assert manager.config.LIMITE_MAXIMO == 25
    assert manager.ultima_chamada is None

def test_init_custom_config(custom_config):
    """Testa inicialização com configuração customizada."""
    manager = ChamadasSequenciaisManager(config=custom_config)
    assert manager.config.LIMITE_AVISO == 15
    assert manager.config.LIMITE_MAXIMO == 20
    assert manager.config.NIVEIS_ALERTA == [5, 10, 15, 18]

def test_registrar_chamada_simples(temp_storage):
    """Testa registro de chamada simples."""
    manager = ChamadasSequenciaisManager(storage_path=temp_storage)
    
    # Primeira chamada não deve gerar aviso
    result = manager.registrar_chamada()
    assert result is None
    assert manager.contador == 1
    assert manager.ultima_chamada is not None

@pytest.mark.asyncio
async def test_alertas_graduais(temp_storage, custom_config):
    """Testa sistema de alertas graduais."""
    manager = ChamadasSequenciaisManager(config=custom_config, storage_path=temp_storage)
    
    # Mock do embate_manager
    manager.embate_manager = MagicMock()
    manager.embate_manager.create_embate.return_value = {"id": "test-123"}
    
    # Testa cada nível de alerta
    alertas = []
    for _ in range(20):
        result = await manager.registrar_chamada()
        if result:
            alertas.append(result)
    
    assert len(alertas) == 4  # Um para cada nível
    
    # Verifica progressão de severidade
    assert alertas[0]["severidade"] == "baixa"
    assert alertas[1]["severidade"] == "média"
    assert alertas[2]["severidade"] == "alta"
    assert alertas[3]["severidade"] == "alta"
    
    # Verifica sugestões
    assert len(alertas[-1]["sugestoes"]) > len(alertas[0]["sugestoes"])

def test_backup_estado(temp_storage, custom_config):
    """Testa sistema de backup."""
    manager = ChamadasSequenciaisManager(config=custom_config, storage_path=temp_storage)
    
    # Gera alguns backups
    for _ in range(10):
        manager.registrar_chamada()
        
    # Verifica se backups foram criados
    backups = []
    for f in os.listdir(os.path.dirname(temp_storage)):
        if f.endswith('.bak'):
            backups.append(f)
            
    assert len(backups) == custom_config.MAX_BACKUP_FILES

def test_migracao_versao(temp_storage):
    """Testa migração de versão do estado."""
    # Cria estado antigo
    estado_v1 = {
        "contador": 5,
        "ultima_chamada": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    with open(temp_storage, "w") as f:
        json.dump(estado_v1, f)
        
    # Inicializa manager que deve migrar
    manager = ChamadasSequenciaisManager(storage_path=temp_storage)
    
    # Verifica se backup foi criado
    backups = [f for f in os.listdir(os.path.dirname(temp_storage)) if f.endswith('.bak')]
    assert len(backups) == 1
    
    # Verifica se estado foi mantido
    assert manager.contador == 5

def test_metricas_prometheus(temp_storage):
    """Testa atualização de métricas Prometheus."""
    manager = ChamadasSequenciaisManager(storage_path=temp_storage)
    
    # Registra algumas chamadas
    for _ in range(5):
        manager.registrar_chamada()
        
    # Verifica contadores
    assert manager.CHAMADAS_COUNTER._value.get() == 5
    assert manager.CONTADOR_ATUAL._value.get() == 5
    
    # Reseta e verifica atualização
    manager.resetar()
    assert manager.CONTADOR_ATUAL._value.get() == 0

def test_reset_por_tempo(temp_storage, custom_config):
    """Testa reset do contador por tempo."""
    manager = ChamadasSequenciaisManager(config=custom_config, storage_path=temp_storage)
    
    # Registra algumas chamadas
    for _ in range(5):
        manager.registrar_chamada()
        
    assert manager.contador == 5
    
    # Simula passagem de tempo
    manager.ultima_chamada = datetime.now() - timedelta(seconds=custom_config.TEMPO_RESET + 1)
    
    # Próxima chamada deve resetar contador
    manager.registrar_chamada()
    assert manager.contador == 1

def test_persistencia_estado(temp_storage):
    """Testa persistência do estado entre instâncias."""
    # Primeira instância
    manager1 = ChamadasSequenciaisManager(storage_path=temp_storage)
    for _ in range(5):
        manager1.registrar_chamada()
        
    # Segunda instância deve carregar estado
    manager2 = ChamadasSequenciaisManager(storage_path=temp_storage)
    assert manager2.contador == 5
    assert manager2.ultima_chamada is not None
    
    # Verifica versão
    with open(temp_storage) as f:
        estado = json.load(f)
        assert estado["version"] == manager1.config.VERSION

@pytest.mark.asyncio
async def test_erro_criacao_embate(temp_storage):
    """Testa tratamento de erro na criação de embate."""
    manager = ChamadasSequenciaisManager(storage_path=temp_storage)
    
    # Mock do embate_manager com erro
    manager.embate_manager = MagicMock()
    manager.embate_manager.create_embate.side_effect = Exception("Erro teste")
    
    # Força contador para gerar alerta
    manager.contador = 20
    result = await manager._criar_alerta(20)
    
    # Mesmo com erro deve retornar resultado
    assert result["tipo"] == "aviso"
    assert result["embate_id"] is None

def test_erro_backup(temp_storage, custom_config):
    """Testa tratamento de erro no backup."""
    manager = ChamadasSequenciaisManager(config=custom_config, storage_path=temp_storage)
    
    # Remove permissão de escrita
    os.chmod(os.path.dirname(temp_storage), 0o444)
    
    try:
        # Deve continuar funcionando mesmo sem poder fazer backup
        manager.registrar_chamada()
        assert manager.contador == 1
    finally:
        # Restaura permissão
        os.chmod(os.path.dirname(temp_storage), 0o777) 