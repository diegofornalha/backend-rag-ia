import pytest
from datetime import datetime
from ..config.embates_config import EmbatesConfig
from ..monitoring.unified_monitor import UnifiedMonitor
from ..protection.unified_protection import UnifiedProtection

@pytest.fixture
def config():
    return EmbatesConfig()

@pytest.fixture
def monitor(config):
    return UnifiedMonitor(config)

@pytest.fixture
def protection(config):
    return UnifiedProtection(config)

def test_config_defaults(config):
    """Testa valores padrão da configuração"""
    assert config.MAX_TOOLS_PER_EMBATE == 3
    assert config.WARNING_THRESHOLD == 2
    assert config.CACHE_TTL_MINUTES == 30
    assert config.MAX_CACHE_ENTRIES == 100

def test_monitor_initialization(monitor):
    """Testa inicialização do monitor"""
    assert monitor.metrics is not None
    assert monitor.cache is not None
    assert monitor.counter is not None

def test_monitor_operation_recording(monitor):
    """Testa registro de operações"""
    monitor.record_operation(
        embate_id='test',
        operation='test_op',
        duration_ms=100.0,
        success=True
    )
    
    stats = monitor.get_statistics()
    assert stats['counter']['total_calls'] == 1
    assert stats['metrics']['total_operations'] == 1

def test_monitor_cache(monitor):
    """Testa funcionalidades de cache"""
    embate = {'id': 'test_cache'}
    result = {'processed': True}
    
    # Inicialmente vazio
    assert monitor.check_cache(embate) is None
    
    # Armazena e verifica
    monitor.store_in_cache(embate, result)
    cached = monitor.check_cache(embate)
    assert cached == result

def test_monitor_rate_limit(monitor):
    """Testa limite de taxa"""
    embate_id = 'test_rate'
    
    # Primeira chamada deve passar
    assert monitor.check_rate_limit(embate_id)
    
    # Registra várias operações
    for _ in range(monitor.config.MAX_CALLS_PER_WINDOW + 1):
        monitor.record_operation(
            embate_id=embate_id,
            operation='test',
            duration_ms=100.0,
            success=True
        )
    
    # Deve bloquear após exceder limite
    assert not monitor.check_rate_limit(embate_id)

def test_protection_basic(protection):
    """Testa proteções básicas"""
    embate = {
        'titulo': 'Teste'
    }
    
    protected = protection.protect_embate(embate)
    
    # Verifica campos protegidos
    assert 'data_inicio' in protected
    assert 'metadata' in protected
    assert 'status' in protected
    assert 'argumentos' in protected
    assert 'tipo' in protected
    assert 'contexto' in protected

def test_protection_validation(protection):
    """Testa validação de embates"""
    # Embate válido
    valid_embate = {
        'titulo': 'Teste Válido',
        'tipo': 'tecnico',
        'contexto': 'Teste',
        'status': 'aberto',
        'data_inicio': datetime.now().isoformat(),
        'argumentos': [],
        'metadata': {
            'impacto': 'médio',
            'prioridade': 'alta',
            'tags': ['teste']
        }
    }
    
    result = protection.validate_embate(valid_embate)
    assert len(result['errors']) == 0
    
    # Embate inválido
    invalid_embate = {
        'titulo': 'Teste Inválido'
    }
    
    result = protection.validate_embate(invalid_embate)
    assert len(result['errors']) > 0

def test_protection_rate_limit(protection):
    """Testa limite de taxa na proteção"""
    embate = {
        'titulo': 'Teste Rate Limit',
        'id': 'test_rate'
    }
    
    # Primeira chamada deve passar
    protection.protect_embate(embate)
    
    # Força limite
    for _ in range(protection.config.MAX_CALLS_PER_WINDOW):
        protection.monitor.record_operation(
            embate_id=embate['id'],
            operation='test',
            duration_ms=100.0,
            success=True
        )
    
    # Deve falhar após exceder limite
    with pytest.raises(ValueError) as exc_info:
        protection.protect_embate(embate)
    assert "Limite de taxa excedido" in str(exc_info.value)

def test_protection_warning(protection):
    """Testa avisos preventivos"""
    embate = {
        'titulo': 'Teste Warning',
        'id': 'test_warning'
    }
    
    # Primeira chamada - sem aviso
    protection.protect_embate(embate)
    assert not protection.monitor.should_warn(embate['id'])
    
    # Segunda chamada - deve avisar
    protection.protect_embate(embate)
    assert protection.monitor.should_warn(embate['id']) 