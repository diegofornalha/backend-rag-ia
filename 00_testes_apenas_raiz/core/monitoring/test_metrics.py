"""
Testes para monitoramento e métricas do sistema.
"""

from datetime import datetime, timedelta

import pytest

from backend_rag_ia.monitoring.metrics import (
    CacheMetric,
    DependencyMetric,
    MetricsCollector,
    ResponseTimeMetric,
    SearchAccuracyMetric,
)


@pytest.fixture
def metrics_collector():
    """Fixture que cria um coletor de métricas para testes."""
    return MetricsCollector()

@pytest.mark.asyncio
async def test_response_time_metric(metrics_collector):
    """Testa métricas de tempo de resposta."""
    metric = ResponseTimeMetric()
    
    # Simula 10 requisições
    for _ in range(10):
        start_time = datetime.now()
        await metric.record_request(start_time, start_time + timedelta(milliseconds=150))
    
    stats = await metric.get_stats()
    assert stats["avg_response_time"] < 200  # Meta: < 200ms
    assert stats["p95_response_time"] < 250  # 95% abaixo de 250ms
    assert stats["p99_response_time"] < 300  # 99% abaixo de 300ms

@pytest.mark.asyncio
async def test_cache_hit_rate(metrics_collector):
    """Testa métricas de cache hit rate."""
    metric = CacheMetric()
    
    # Simula 100 acessos ao cache
    for _ in range(80):  # 80 hits
        await metric.record_hit()
    for _ in range(20):  # 20 misses
        await metric.record_miss()
    
    stats = await metric.get_stats()
    assert stats["hit_rate"] > 0.8  # Meta: > 80%
    assert stats["total_requests"] == 100
    assert stats["hits"] == 80
    assert stats["misses"] == 20

@pytest.mark.asyncio
async def test_search_accuracy(metrics_collector):
    """Testa métricas de precisão da busca."""
    metric = SearchAccuracyMetric()
    
    # Simula 100 buscas
    for _ in range(92):  # 92 relevantes
        await metric.record_relevant_result()
    for _ in range(8):  # 8 irrelevantes
        await metric.record_irrelevant_result()
    
    stats = await metric.get_stats()
    assert stats["accuracy"] > 0.9  # Meta: > 90%
    assert stats["total_searches"] == 100
    assert stats["relevant_results"] == 92
    assert stats["irrelevant_results"] == 8

@pytest.mark.asyncio
async def test_dependency_check(metrics_collector):
    """Testa verificação de dependências."""
    metric = DependencyMetric()
    
    # Simula verificação de dependências
    await metric.check_dependencies()
    
    stats = await metric.get_stats()
    assert stats["conflicts"] == 0  # Meta: zero conflitos
    assert stats["outdated"] == []  # Sem dependências desatualizadas
    assert stats["incompatible"] == []  # Sem incompatibilidades

@pytest.mark.asyncio
async def test_metrics_aggregation(metrics_collector):
    """Testa agregação de todas as métricas."""
    # Coleta todas as métricas
    await metrics_collector.collect_all()
    
    # Verifica agregação
    report = await metrics_collector.generate_report()
    assert "response_time" in report
    assert "cache" in report
    assert "search" in report
    assert "dependencies" in report
    
    # Verifica alertas
    alerts = await metrics_collector.check_alerts()
    assert len(alerts) == 0  # Não deve ter alertas críticos 