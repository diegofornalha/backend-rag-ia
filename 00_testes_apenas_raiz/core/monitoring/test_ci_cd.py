"""
Testes para CI/CD e automação.
"""


import pytest

from backend_rag_ia.monitoring.ci_cd import (
    DependencyResolver,
    PipelineValidator,
    RuffChecker,
    TestRunner,
)


@pytest.fixture
def pipeline_validator():
    """Fixture que cria um validador de pipeline para testes."""
    return PipelineValidator()

@pytest.mark.asyncio
async def test_ruff_integration(pipeline_validator):
    """Testa integração com Ruff."""
    checker = RuffChecker()
    
    # Verifica código
    results = await checker.check_code()
    assert results["errors"] == 0  # Não deve ter erros
    assert results["warnings"] == []  # Não deve ter warnings
    
    # Verifica correções automáticas
    fixes = await checker.auto_fix()
    assert fixes["applied"] >= 0  # Número de correções aplicadas
    assert fixes["failed"] == 0  # Não deve ter falhas
    
    # Verifica regras personalizadas
    custom_rules = await checker.get_custom_rules()
    assert len(custom_rules) > 0  # Deve ter regras definidas

@pytest.mark.asyncio
async def test_automated_tests(pipeline_validator):
    """Testa execução automatizada de testes."""
    runner = TestRunner()
    
    # Executa testes
    results = await runner.run_all()
    assert results["passed"] > 0  # Deve ter testes passando
    assert results["failed"] == 0  # Não deve ter falhas
    assert results["coverage"] > 80  # Cobertura > 80%
    
    # Verifica relatórios
    reports = await runner.generate_reports()
    assert "coverage" in reports
    assert "test_results" in reports
    assert "performance" in reports

@pytest.mark.asyncio
async def test_dependency_resolution(pipeline_validator):
    """Testa resolução de dependências."""
    resolver = DependencyResolver()
    
    # Verifica dependências
    results = await resolver.check_all()
    assert results["conflicts"] == 0  # Não deve ter conflitos
    assert results["outdated"] == []  # Não deve ter pacotes desatualizados
    
    # Testa resolução automática
    resolution = await resolver.auto_resolve()
    assert resolution["success"]  # Deve resolver com sucesso
    assert resolution["errors"] == []  # Não deve ter erros

@pytest.mark.asyncio
async def test_build_validation(pipeline_validator):
    """Testa validação de build."""
    # Verifica build
    build = await pipeline_validator.validate_build()
    assert build["status"] == "green"  # Build deve estar verde
    assert build["errors"] == []  # Não deve ter erros
    
    # Verifica artefatos
    artifacts = await pipeline_validator.check_artifacts()
    assert len(artifacts) > 0  # Deve gerar artefatos
    assert all(a["valid"] for a in artifacts)  # Todos devem ser válidos

@pytest.mark.asyncio
async def test_pipeline_metrics(pipeline_validator):
    """Testa métricas do pipeline."""
    # Coleta métricas
    metrics = await pipeline_validator.collect_metrics()
    
    # Verifica tempos
    assert metrics["avg_build_time"] < 300  # < 5 minutos
    assert metrics["avg_test_time"] < 120  # < 2 minutos
    
    # Verifica sucesso
    assert metrics["success_rate"] > 0.95  # > 95% sucesso
    assert metrics["failed_builds"] == []  # Não deve ter falhas 