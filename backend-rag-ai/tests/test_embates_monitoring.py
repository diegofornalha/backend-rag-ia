import pytest
from datetime import datetime, timedelta
from backend_rag_ai_py.monitoring.embates_counter import GlobalEmbatesCounter
from backend_rag_ai_py.monitoring.embates_cache import EmbatesCache
from backend_rag_ai_py.monitoring.embates_metrics import EmbatesMetrics, EmbateMetric
from backend_rag_ai_py.monitoring.embates_protection_manager import EmbatesProtectionManager

@pytest.fixture
def counter():
    return GlobalEmbatesCounter()

@pytest.fixture
def cache():
    return EmbatesCache(cache_ttl_minutes=1)

@pytest.fixture
def metrics():
    return EmbatesMetrics(max_history=10)

@pytest.fixture
def manager():
    return EmbatesProtectionManager()

def test_counter_basic(counter):
    """Testa funcionalidades básicas do contador"""
    counter.increment('test1')
    counter.increment('test1')
    counter.increment('test2')
    
    assert counter.get_total_calls() == 3
    assert counter.get_embate_calls('test1') == 2
    assert counter.get_embate_calls('test2') == 1
    
def test_counter_statistics(counter):
    """Testa estatísticas do contador"""
    for i in range(5):
        counter.increment(f'test_{i}')
    counter.increment('test_0')  # Mais uma chamada para test_0
    
    stats = counter.get_statistics()
    assert stats['total_calls'] == 6
    assert stats['unique_embates'] == 5
    assert stats['most_active_embate'][0] == 'test_0'
    assert stats['most_active_embate'][1] == 2
    
def test_cache_basic(cache):
    """Testa funcionalidades básicas do cache"""
    embate = {'id': 'test', 'data': 'value'}
    result = {'processed': True}
    
    # Inicialmente não deve ter cache
    assert cache.get_validation_result(embate) is None
    
    # Armazena e verifica
    cache.store_validation(embate, result)
    cached = cache.get_validation_result(embate)
    assert cached == result
    
def test_cache_ttl(cache):
    """Testa TTL do cache"""
    embate = {'id': 'test_ttl'}
    result = {'processed': True}
    
    cache.store_validation(embate, result)
    assert cache.get_validation_result(embate) == result
    
    # Força expiração modificando TTL
    cache._ttl = timedelta(minutes=-1)
    assert cache.get_validation_result(embate) is None
    
def test_cache_statistics(cache):
    """Testa estatísticas do cache"""
    for i in range(3):
        embate = {'id': f'test_{i}'}
        cache.store_validation(embate, {'result': i})
    
    stats = cache.get_statistics()
    assert stats['total_entries'] == 3
    assert stats['valid_entries'] == 3
    assert stats['invalid_entries'] == 0
    
def test_metrics_basic(metrics):
    """Testa funcionalidades básicas das métricas"""
    metric = EmbateMetric(
        timestamp=datetime.now(),
        embate_id='test',
        operation='test_op',
        duration_ms=100.0,
        success=True
    )
    
    metrics.record_operation(metric)
    assert len(metrics.metrics) == 1
    assert metrics.metrics[0].embate_id == 'test'
    
def test_metrics_statistics(metrics):
    """Testa estatísticas das métricas"""
    # Sucesso
    metrics.record_operation(EmbateMetric(
        timestamp=datetime.now(),
        embate_id='test1',
        operation='op1',
        duration_ms=100.0,
        success=True
    ))
    
    # Erro
    metrics.record_operation(EmbateMetric(
        timestamp=datetime.now(),
        embate_id='test2',
        operation='op2',
        duration_ms=200.0,
        success=False,
        error_type='ValueError'
    ))
    
    stats = metrics.get_statistics()
    assert stats['total_operations'] == 2
    assert stats['success_rate'] == 0.5
    assert stats['avg_duration_ms'] == 150.0
    assert stats['error_distribution']['ValueError'] == 1
    
def test_manager_integration(manager):
    """Testa integração completa no manager"""
    embate = {
        'titulo': 'Teste Integração',
        'tipo': 'tecnico'
    }
    
    # Primeira chamada - deve processar normalmente
    result1 = manager.process_embate(embate)
    
    # Segunda chamada - deve usar cache
    result2 = manager.process_embate(embate)
    
    # Verifica resultados
    assert result1 == result2
    
    # Verifica estatísticas
    stats = manager.get_statistics()
    assert stats['counter']['total_calls'] == 2
    assert stats['cache']['total_entries'] >= 1
    assert stats['metrics']['total_operations'] >= 2
    
def test_manager_error_handling(manager):
    """Testa tratamento de erros no manager"""
    embate_invalido = {
        'titulo': 'Teste Erro',
        'tools_count': 4  # Excede limite
    }
    
    with pytest.raises(ValueError):
        manager.process_embate(embate_invalido)
    
    # Verifica se erro foi registrado
    stats = manager.get_statistics()
    assert any(
        error_type == 'ValueError' 
        for error_type in stats['metrics']['error_distribution'].keys()
    )
    
def test_manager_performance(manager):
    """Testa performance do manager com cache"""
    embate = {
        'titulo': 'Teste Performance',
        'tipo': 'tecnico'
    }
    
    # Primeira chamada - sem cache
    start = datetime.now()
    manager.process_embate(embate)
    first_duration = (datetime.now() - start).total_seconds()
    
    # Segunda chamada - com cache
    start = datetime.now()
    manager.process_embate(embate)
    second_duration = (datetime.now() - start).total_seconds()
    
    # Cache deve ser mais rápido
    assert second_duration < first_duration 