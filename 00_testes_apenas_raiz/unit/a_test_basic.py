import importlib.util

import pytest


def test_environment():
    """Teste básico para verificar se o ambiente está funcionando"""
    required_packages = [
        "pgvector",
        "sentence_transformers",
        "torch",
        "transformers"
    ]
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            pytest.fail(f"Pacote {package} não está instalado")
    
    assert True 