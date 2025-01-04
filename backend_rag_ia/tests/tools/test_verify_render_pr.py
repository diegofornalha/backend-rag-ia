<<<<<<< Updated upstream
"""Implementa testes para validação de PRs no Render.

Este módulo contém testes para verificar a validação de configurações
do Render, incluindo render.yaml, Dockerfile e health checks.
"""

=======
>>>>>>> Stashed changes
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from backend_rag_ia.tools.verify_render_pr import RenderPRValidator, RenderValidationResult


@pytest.fixture
def validator():
    """Cria um validador de PR com configurações mockadas.

    Returns
    -------
    RenderPRValidator
        Instância do validador configurada para testes.

    """
    with patch('backend_rag_ia.tools.verify_render_pr.get_settings') as mock_settings:
        # Mock das configurações
        mock_settings.return_value = Mock(
            is_preview_environment=True,
            cors_origins_list=["http://localhost:3000"],
            active_url="http://localhost:8000"
        )
        yield RenderPRValidator()

@pytest.fixture
def valid_render_yaml():
    """Retorna um render.yaml válido para testes.

    Returns
    -------
    str
        Conteúdo válido do render.yaml.

    """
    return """
services:
  - type: web
    name: backend-rag-ia
    env: docker
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
previews:
  enable: true
"""

@pytest.fixture
def valid_dockerfile():
    """Retorna um Dockerfile válido para testes.

    Returns
    -------
    str
        Conteúdo válido do Dockerfile.

    """
    return """
FROM python:3.11
WORKDIR /app
ENV PYTHONPATH=/app
ENV PORT=8000
"""

def test_validate_render_yaml_success(validator, valid_render_yaml):
    """Testa validação bem-sucedida do render.yaml.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.
    valid_render_yaml : str
        Conteúdo válido do render.yaml.

    """
    with patch("builtins.open", mock_open(read_data=valid_render_yaml)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            assert validator.validate_render_yaml() is True
            assert not validator.errors

def test_validate_render_yaml_missing_file(validator):
    """Testa quando render.yaml não existe.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    with patch.object(Path, "exists") as mock_exists:
        mock_exists.return_value = False
        assert validator.validate_render_yaml() is False
        assert "render.yaml não encontrado" in validator.errors[0]

def test_validate_render_yaml_invalid_content(validator):
    """Testa render.yaml com conteúdo inválido.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    invalid_yaml = "invalid: yaml: content:"
    with patch("builtins.open", mock_open(read_data=invalid_yaml)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            assert validator.validate_render_yaml() is False
            assert any("Erro ao ler render.yaml" in error for error in validator.errors)

def test_validate_settings_success(validator):
    """Testa validação bem-sucedida das configurações.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    assert validator.validate_settings() is True
    assert not validator.errors

def test_validate_docker_setup_success(validator, valid_dockerfile):
    """Testa validação bem-sucedida do Dockerfile.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.
    valid_dockerfile : str
        Conteúdo válido do Dockerfile.

    """
    with patch("builtins.open", mock_open(read_data=valid_dockerfile)):
        with patch.object(Path, "exists") as mock_exists:
            mock_exists.return_value = True
            assert validator.validate_docker_setup() is True
            assert not validator.errors

def test_validate_health_check_success(validator):
    """Testa health check bem-sucedido.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=200)
        assert validator.validate_health_check() is True
        assert not validator.errors

def test_validate_health_check_failure(validator):
    """Testa falha no health check.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    with patch("requests.get") as mock_get:
        mock_get.return_value = Mock(status_code=500)
        assert validator.validate_health_check() is False
        assert any("Health check falhou" in error for error in validator.errors)

def test_run_validation_all_success(validator):
    """Testa execução completa com sucesso.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    with patch.multiple(validator,
                       validate_render_yaml=Mock(return_value=True),
                       validate_settings=Mock(return_value=True),
                       validate_docker_setup=Mock(return_value=True),
                       validate_health_check=Mock(return_value=True)):
        result = validator.run_validation()
        assert isinstance(result, RenderValidationResult)
        assert result.is_valid
        assert not result.errors
        assert len(result.suggestions) > 0

def test_run_validation_with_errors(validator):
    """Testa execução com erros.

    Parameters
    ----------
    validator : RenderPRValidator
        Instância do validador.

    """
    with patch.multiple(validator,
                       validate_render_yaml=Mock(return_value=False),
                       validate_settings=Mock(return_value=True),
                       validate_docker_setup=Mock(return_value=True),
                       validate_health_check=Mock(return_value=True)):
        validator.errors.append("Erro teste")
        result = validator.run_validation()
        assert not result.is_valid
        assert "Erro teste" in result.errors
