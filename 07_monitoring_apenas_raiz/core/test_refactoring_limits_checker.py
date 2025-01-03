"""Testes para o RefactoringLimitsChecker."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from .refactoring_limits_checker import RefactoringLimitsChecker
from .refactoring_metrics import CodeMetrics

@pytest.fixture
def temp_dir(tmp_path):
    """Cria diretório temporário para testes."""
    return tmp_path

@pytest.fixture
def config_file(temp_dir):
    """Cria arquivo de configuração para testes."""
    config = {
        "max_iterations": 3,
        "min_impact_per_change": 0.2,
        "max_consolidated_ratio": 0.8,
        "diminishing_returns_threshold": 0.5,
        "max_complexity": 10,
        "min_cohesion": 0.6,
        "max_coupling": 0.5,
        "max_dependencies": 15
    }
    
    config_path = temp_dir / "refactoring_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f)
        
    return config_path

@pytest.fixture
def checker(temp_dir, config_file):
    """Cria instância do RefactoringLimitsChecker."""
    return RefactoringLimitsChecker(project_root=temp_dir)

def test_first_iteration(checker):
    """Testa primeira iteração de refatoração."""
    metrics = {
        "removed": 2,
        "simplified": 3,
        "consolidated": 1,
        "updated": 4,
        "total_changes": 10,
        "iterations": 1
    }
    
    result = checker.should_continue_refactoring(metrics)
    assert result["continue"] is True
    assert "Primeira iteração" in result["reason"]

def test_max_iterations(checker):
    """Testa limite máximo de iterações."""
    # Primeira iteração
    result1 = checker.should_continue_refactoring({
        "removed": 2,
        "simplified": 3,
        "consolidated": 1,
        "updated": 4,
        "total_changes": 10,
        "iterations": 1
    })
    assert result1["continue"] is True
    
    # Segunda iteração
    result2 = checker.should_continue_refactoring({
        "removed": 1,
        "simplified": 2,
        "consolidated": 1,
        "updated": 3,
        "total_changes": 7,
        "iterations": 2
    })
    assert result2["continue"] is True
    
    # Terceira iteração (limite)
    result3 = checker.should_continue_refactoring({
        "removed": 1,
        "simplified": 1,
        "consolidated": 1,
        "updated": 2,
        "total_changes": 5,
        "iterations": 3
    })
    assert result3["continue"] is False
    assert "limite máximo de iterações" in result3["reason"]

def test_excessive_consolidation(checker):
    """Testa detecção de consolidação excessiva."""
    # Primeira iteração normal
    checker.should_continue_refactoring({
        "removed": 2,
        "simplified": 3,
        "consolidated": 1,
        "updated": 4,
        "total_changes": 10,
        "iterations": 1
    })
    
    # Segunda iteração com consolidação excessiva
    metrics = {
        "removed": 1,
        "simplified": 1,
        "consolidated": 9,  # 90% consolidação
        "updated": 1,
        "total_changes": 10,
        "iterations": 2  # Mantém abaixo do limite de iterações
    }
    
    result = checker.should_continue_refactoring(metrics)
    assert result["continue"] is False
    assert "consolidação" in result["reason"].lower()

def test_diminishing_returns(checker):
    """Testa detecção de retornos diminutos."""
    # Primeira iteração
    checker.should_continue_refactoring({
        "removed": 5,
        "simplified": 5,
        "consolidated": 2,
        "updated": 8,
        "total_changes": 20,
        "iterations": 1,
        "complexity": 10,
        "cohesion": 0.5
    })
    
    # Segunda iteração
    checker.should_continue_refactoring({
        "removed": 3,
        "simplified": 3,
        "consolidated": 1,
        "updated": 5,
        "total_changes": 12,
        "iterations": 2,
        "complexity": 8,
        "cohesion": 0.6
    })
    
    # Terceira iteração (pouca melhoria)
    result = checker.should_continue_refactoring({
        "removed": 1,
        "simplified": 1,
        "consolidated": 1,
        "updated": 2,
        "total_changes": 5,
        "iterations": 2,  # Mantém abaixo do limite
        "complexity": 7,
        "cohesion": 0.65
    })
    
    assert result["continue"] is False
    assert "diminutos" in result["reason"].lower()

def test_code_metrics_violation(checker):
    """Testa violação de métricas de código."""
    code_metrics = CodeMetrics(
        cyclomatic_complexity=15,  # Acima do limite
        module_cohesion=0.4,       # Abaixo do limite
        coupling_score=0.6,        # Acima do limite
        dependencies=set(range(20)), # Acima do limite
        loc=100
    )
    
    result = checker.process_event(
        event_type="code",
        content="test content",
        metrics={
            "file_path": "test.py"
        }
    )
    
    with patch('pathlib.Path.open'), \
         patch('ast.parse'), \
         patch.object(checker.metrics_analyzer, 'analyze_file', return_value=code_metrics):
        
        result = checker.process_event(
            event_type="code",
            content="test content",
            metrics={
                "file_path": "test.py"
            }
        )
        assert result["continue"] is False
        assert all(x in result["reason"].lower() for x in ["complexidade", "coesão", "acoplamento"])

def test_semantic_changes_violation(checker):
    """Testa violação de mudanças semânticas."""
    semantic_changes = {
        "complexity_changes": {
            "complexity_delta": 6  # Acima do limite
        },
        "api_changes": {
            "breaking_changes": ["removed func1", "changed func2", "removed func3"]  # Acima do limite
        }
    }
    
    with patch('pathlib.Path.open'), \
         patch('ast.parse'), \
         patch.object(checker.metrics_analyzer, 'analyze_file',
                     return_value=CodeMetrics(5, 0.7, 0.3, set(), 100)), \
         patch.object(checker.semantic_analyzer, 'analyze_changes',
                     return_value=semantic_changes):
        
        result = checker.process_event(
            event_type="code",
            content="test content",
            metrics={
                "file_path": "test.py",
                "old_content": "old code",
                "new_content": "new code"
            }
        )
        assert result["continue"] is False
        assert "complexidade" in result["reason"].lower()
        assert "breaking changes" in result["reason"].lower()

def test_recommendations(checker):
    """Testa geração de recomendações."""
    # Simula algumas métricas
    checker.history = [{
        "removed": 5,
        "simplified": 2,
        "consolidated": 8,
        "updated": 3,
        "total_changes": 18,
        "iterations": 1
    }]
    
    # Simula métricas de arquivo
    checker.file_metrics = {
        "test.py": CodeMetrics(
            cyclomatic_complexity=9,  # Próximo do limite
            module_cohesion=0.65,     # OK
            coupling_score=0.45,      # Próximo do limite
            dependencies=set(range(12)), # OK
            loc=100
        )
    }
    
    recommendations = checker.get_recommendations()
    assert len(recommendations) > 0
    assert any("simplificar" in r.lower() for r in recommendations)
    assert any("consolidação" in r.lower() for r in recommendations)
    assert any("complexidade" in r.lower() for r in recommendations)

def test_custom_thresholds(checker):
    """Testa carregamento de thresholds customizados."""
    assert checker.thresholds["max_iterations"] == 3  # Do arquivo de config
    assert checker.thresholds["max_complexity"] == 10  # Do arquivo de config
    assert checker.thresholds["min_cohesion"] == 0.6  # Do arquivo de config

def test_history_persistence(checker, temp_dir):
    """Testa persistência do histórico."""
    metrics = {
        "removed": 2,
        "simplified": 3,
        "consolidated": 1,
        "updated": 4,
        "total_changes": 10,
        "iterations": 1
    }
    
    checker.should_continue_refactoring(metrics)
    
    # Verifica se arquivo foi criado
    history_file = temp_dir / "refactoring_history.json"
    assert history_file.exists()
    
    # Verifica conteúdo
    with open(history_file) as f:
        saved_history = json.load(f)
        assert len(saved_history) == 1
        assert saved_history[0] == metrics

def test_invalid_config(temp_dir):
    """Testa comportamento com arquivo de config inválido."""
    # Cria arquivo de config inválido
    config_path = temp_dir / "refactoring_config.json"
    with open(config_path, 'w') as f:
        f.write("invalid json")
        
    # Deve usar valores default
    checker = RefactoringLimitsChecker(project_root=temp_dir)
    assert checker.thresholds["max_iterations"] == 5  # Valor default
    assert checker.thresholds["max_complexity"] == 15  # Valor default 