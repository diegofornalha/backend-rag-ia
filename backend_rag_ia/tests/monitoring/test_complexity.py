"""
Testes para o verificador de complexidade.
"""

import pytest
from datetime import datetime
from backend_rag_ia.monitoring.complexity_checker import ComplexityChecker, ComplexityMetrics

@pytest.fixture
def complexity_checker():
    """Fixture que cria um verificador de complexidade para testes."""
    return ComplexityChecker()

@pytest.mark.asyncio
async def test_complexity_metrics(complexity_checker):
    """Testa coleta de métricas de complexidade."""
    metrics = await complexity_checker.check_complexity()
    
    assert isinstance(metrics, ComplexityMetrics)
    assert 0 <= metrics.dependencies_count <= 100
    assert 0 <= metrics.integration_points <= 50
    assert 0 <= metrics.maintenance_score <= 1
    assert 0 <= metrics.stability_score <= 1
    assert 0 <= metrics.understanding_score <= 1

@pytest.mark.asyncio
async def test_threshold_warnings(complexity_checker):
    """Testa geração de warnings quando limites são excedidos."""
    # Força métricas ruins para gerar warnings
    complexity_checker.thresholds.update({
        "max_dependencies": 10,
        "max_integration_points": 5,
        "min_maintenance_score": 0.9,
        "min_stability_score": 0.9,
        "min_understanding_score": 0.9
    })
    
    await complexity_checker.check_complexity()
    
    # Deve gerar warnings para todas as métricas
    assert len(complexity_checker.warnings) == 5
    warning_types = {w["type"] for w in complexity_checker.warnings}
    assert warning_types == {
        "dependencies", 
        "integrations", 
        "maintenance", 
        "stability", 
        "understanding"
    }

@pytest.mark.asyncio
async def test_recommendations(complexity_checker):
    """Testa geração de recomendações."""
    # Força alguns warnings
    complexity_checker.warnings = [
        {
            "type": "dependencies",
            "message": "Muitas dependências",
            "timestamp": datetime.now()
        },
        {
            "type": "maintenance",
            "message": "Baixa manutenibilidade",
            "timestamp": datetime.now()
        }
    ]
    
    recommendations = await complexity_checker.get_recommendations()
    
    assert len(recommendations) == 2
    assert any("dependências" in r.lower() for r in recommendations)
    assert any("manutenibilidade" in r.lower() for r in recommendations)

@pytest.mark.asyncio
async def test_should_stop_development(complexity_checker):
    """Testa decisão de parar desenvolvimento."""
    # Cenário 1: Sem warnings
    assert not await complexity_checker.should_stop_development()
    
    # Cenário 2: Muitos warnings
    complexity_checker.warnings = [
        {"type": "dependencies", "message": "Warning 1", "timestamp": datetime.now()},
        {"type": "integrations", "message": "Warning 2", "timestamp": datetime.now()},
        {"type": "maintenance", "message": "Warning 3", "timestamp": datetime.now()},
        {"type": "stability", "message": "Warning 4", "timestamp": datetime.now()}
    ]
    assert await complexity_checker.should_stop_development()
    
    # Cenário 3: Scores muito baixos
    complexity_checker.warnings = []
    complexity_checker.thresholds.update({
        "min_maintenance_score": 1.0,  # Força score abaixo de 60%
        "min_stability_score": 1.0,
        "min_understanding_score": 1.0
    })
    assert await complexity_checker.should_stop_development()
    
    # Cenário 4: Limites muito excedidos
    complexity_checker.warnings = []
    complexity_checker.thresholds.update({
        "max_dependencies": 5,  # Força exceder em 50%
        "max_integration_points": 5
    })
    assert await complexity_checker.should_stop_development()

@pytest.mark.asyncio
async def test_complexity_tracking_over_time(complexity_checker):
    """Testa tracking de complexidade ao longo do tempo."""
    # Primeira verificação
    metrics1 = await complexity_checker.check_complexity()
    timestamp1 = complexity_checker.last_check
    
    # Segunda verificação
    metrics2 = await complexity_checker.check_complexity()
    timestamp2 = complexity_checker.last_check
    
    # Verifica timestamps
    assert timestamp1 < timestamp2
    
    # Verifica consistência das métricas
    assert isinstance(metrics1, ComplexityMetrics)
    assert isinstance(metrics2, ComplexityMetrics)
    
    # As métricas não devem variar muito entre verificações próximas
    assert abs(metrics1.maintenance_score - metrics2.maintenance_score) < 0.1
    assert abs(metrics1.stability_score - metrics2.stability_score) < 0.1
    assert abs(metrics1.understanding_score - metrics2.understanding_score) < 0.1 