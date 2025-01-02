"""
Testes para qualidade das buscas e métricas relacionadas.
"""

import pytest
from datetime import datetime, timedelta
from backend_rag_ia.monitoring.search_quality import (
    SearchQualityMonitor,
    RelevanceMetric,
    PrecisionMetric,
    RecallMetric,
    LatencyMetric,
    UserFeedbackMetric
)

@pytest.fixture
def quality_monitor():
    """Fixture que cria um monitor de qualidade para testes."""
    return SearchQualityMonitor()

@pytest.mark.asyncio
async def test_search_relevance(quality_monitor):
    """Testa métricas de relevância da busca."""
    metric = RelevanceMetric()
    
    # Simula 100 buscas com diferentes níveis de relevância
    relevance_scores = [
        1.0, 1.0, 0.9, 0.8, 0.7,  # Muito relevantes
        0.9, 0.8, 0.7, 0.6, 0.5,  # Relevantes
        0.4, 0.3, 0.2, 0.1, 0.0   # Pouco relevantes
    ]
    
    for score in relevance_scores:
        await metric.record_relevance_score(score)
    
    stats = await metric.get_stats()
    assert stats["avg_relevance"] > 0.7  # Meta: relevância média > 70%
    assert stats["high_relevance_ratio"] > 0.6  # Meta: 60% com alta relevância
    assert stats["low_relevance_ratio"] < 0.2  # Meta: menos de 20% com baixa relevância

@pytest.mark.asyncio
async def test_search_precision(quality_monitor):
    """Testa métricas de precisão da busca."""
    metric = PrecisionMetric()
    
    # Simula resultados de busca
    for _ in range(80):  # 80 resultados relevantes
        await metric.record_relevant_result()
    for _ in range(20):  # 20 resultados irrelevantes
        await metric.record_irrelevant_result()
    
    stats = await metric.get_stats()
    assert stats["precision"] > 0.8  # Meta: precisão > 80%
    assert stats["false_positives"] < 20  # Meta: menos de 20 falsos positivos
    assert stats["precision_at_k"][5] > 0.9  # Meta: precisão@5 > 90%

@pytest.mark.asyncio
async def test_search_recall(quality_monitor):
    """Testa métricas de recall da busca."""
    metric = RecallMetric()
    
    # Simula conjunto de resultados esperados vs encontrados
    total_relevant = 100
    found_relevant = 85
    
    await metric.record_search_results(found_relevant, total_relevant)
    
    stats = await metric.get_stats()
    assert stats["recall"] > 0.85  # Meta: recall > 85%
    assert stats["missed_results"] < 15  # Meta: menos de 15 resultados perdidos
    assert stats["recall_at_k"][10] > 0.7  # Meta: recall@10 > 70%

@pytest.mark.asyncio
async def test_search_latency(quality_monitor):
    """Testa métricas de latência da busca."""
    metric = LatencyMetric()
    
    # Simula 100 buscas com diferentes tempos
    for _ in range(100):
        latency = timedelta(milliseconds=150)  # Simulando latência de 150ms
        await metric.record_search_latency(latency)
    
    stats = await metric.get_stats()
    assert stats["avg_latency"] < 200  # Meta: latência média < 200ms
    assert stats["p95_latency"] < 250  # Meta: p95 < 250ms
    assert stats["p99_latency"] < 300  # Meta: p99 < 300ms

@pytest.mark.asyncio
async def test_user_feedback(quality_monitor):
    """Testa métricas de feedback do usuário."""
    metric = UserFeedbackMetric()
    
    # Simula feedback de usuários
    feedbacks = [
        ("positivo", "Resultados muito relevantes"),
        ("positivo", "Encontrou exatamente o que eu precisava"),
        ("neutro", "Resultados ok, mas poderiam ser melhores"),
        ("negativo", "Não encontrou o que eu procurava")
    ]
    
    for tipo, comentario in feedbacks:
        await metric.record_feedback(tipo, comentario)
    
    stats = await metric.get_stats()
    assert stats["satisfaction_rate"] > 0.7  # Meta: satisfação > 70%
    assert stats["positive_feedback_ratio"] > 0.5  # Meta: feedback positivo > 50%
    assert stats["negative_feedback_ratio"] < 0.2  # Meta: feedback negativo < 20%

@pytest.mark.asyncio
async def test_quality_aggregation(quality_monitor):
    """Testa agregação de métricas de qualidade."""
    # Coleta todas as métricas
    await quality_monitor.collect_all_metrics()
    
    # Gera relatório completo
    report = await quality_monitor.generate_quality_report()
    
    # Verifica componentes do relatório
    assert "relevance" in report
    assert "precision" in report
    assert "recall" in report
    assert "latency" in report
    assert "user_feedback" in report
    
    # Verifica KPIs
    kpis = await quality_monitor.get_search_kpis()
    assert kpis["overall_quality_score"] > 0.8  # Meta: qualidade geral > 80%
    assert kpis["user_satisfaction"] > 0.7  # Meta: satisfação > 70%
    assert kpis["performance_score"] > 0.9  # Meta: performance > 90%
    
    # Verifica alertas
    alerts = await quality_monitor.check_quality_alerts()
    assert len(alerts) == 0  # Não deve ter alertas críticos 