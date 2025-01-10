"""
Configurações do pytest para testes do sistema multiagente.
"""

import os
import sys
from typing import Generator

import pytest

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


@pytest.fixture(autouse=True)
def setup_test_env() -> Generator[None, None, None]:
    """Configura o ambiente de teste."""
    # Backup das variáveis originais
    original_env = os.environ.copy()

    # Configura variáveis para teste
    os.environ.update(
        {
            "ENVIRONMENT": "development",
            "OPERATION_MODE": "local",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_KEY": "test-key",
            "GEMINI_API_KEY": "test-key",
        }
    )

    yield

    # Restaura variáveis originais
    os.environ.clear()
    os.environ.update(original_env)
