"""
Testes para fluxo de commit e integração com git.
"""


import pytest

from backend_rag_ia.monitoring.git_flow import (
    BranchManager,
    ChangelogGenerator,
    CommitValidator,
    GitManager,
)


@pytest.fixture
def git_manager():
    """Fixture que cria um gerenciador git para testes."""
    return GitManager()

@pytest.mark.asyncio
async def test_commit_validation(git_manager):
    """Testa validação de commits."""
    validator = CommitValidator()
    
    # Simula mudanças para commit
    changes = {
        "added": [
            "backend_rag_ia/tests/monitoring/test_search_quality.py",
            "backend_rag_ia/monitoring/search_quality.py"
        ],
        "modified": [
            "backend_rag_ia/tests/embates/embate_implementacao_testes.json"
        ],
        "removed": []
    }
    
    # Verifica mudanças
    validation = await validator.validate_changes(changes)
    assert validation["status"] == "valid"
    assert len(validation["warnings"]) == 0
    
    # Verifica mensagem de commit
    commit_msg = "feat(tests): adiciona testes de qualidade de busca"
    msg_validation = await validator.validate_commit_message(commit_msg)
    assert msg_validation["valid"]
    assert msg_validation["type"] == "feat"
    assert msg_validation["scope"] == "tests"

@pytest.mark.asyncio
async def test_branch_management(git_manager):
    """Testa gerenciamento de branches."""
    branch_manager = BranchManager()
    
    # Verifica branch atual
    current = await branch_manager.get_current_branch()
    assert current.startswith("feature/") or current == "main"
    
    # Verifica proteções
    protections = await branch_manager.get_branch_protections("main")
    assert protections["require_reviews"]
    assert protections["require_tests"]
    assert protections["require_up_to_date"]

@pytest.mark.asyncio
async def test_changelog_generation(git_manager):
    """Testa geração de changelog."""
    generator = ChangelogGenerator()
    
    # Gera changelog
    changelog = await generator.generate_for_changes([
        "feat(tests): adiciona testes de qualidade de busca",
        "fix(metrics): corrige cálculo de precisão",
        "docs(readme): atualiza documentação de métricas"
    ])
    
    # Verifica seções
    assert "Features" in changelog
    assert "Bug Fixes" in changelog
    assert "Documentation" in changelog
    
    # Verifica conteúdo
    assert "testes de qualidade de busca" in changelog
    assert "cálculo de precisão" in changelog
    assert "documentação de métricas" in changelog

@pytest.mark.asyncio
async def test_commit_flow(git_manager):
    """Testa fluxo completo de commit."""
    # Prepara mudanças
    changes = {
        "files": [
            "backend_rag_ia/tests/monitoring/test_search_quality.py",
            "backend_rag_ia/tests/embates/embate_implementacao_testes.json"
        ],
        "commit_msg": "feat(tests): adiciona testes de qualidade de busca",
        "branch": "feature/search-quality-tests"
    }
    
    # Executa fluxo
    result = await git_manager.execute_commit_flow(changes)
    
    # Verifica resultado
    assert result["success"]
    assert result["commit_hash"] is not None
    assert len(result["errors"]) == 0
    
    # Verifica hooks
    assert result["pre_commit_passed"]
    assert result["tests_passed"]
    assert result["lint_passed"]

@pytest.mark.asyncio
async def test_commit_hooks(git_manager):
    """Testa hooks de commit."""
    # Configura hooks
    hooks = await git_manager.get_commit_hooks()
    
    # Verifica hooks obrigatórios
    assert "ruff" in hooks
    assert "pytest" in hooks
    assert "black" in hooks
    
    # Executa hooks
    hook_results = await git_manager.run_commit_hooks()
    assert hook_results["passed"]
    assert len(hook_results["failures"]) == 0
    
    # Verifica formatação
    format_results = await git_manager.check_code_formatting()
    assert format_results["formatted"]
    assert len(format_results["issues"]) == 0 