import pytest


def test_environment():
    """Teste básico para verificar se o ambiente está funcionando"""
    try:
        import pgvector
        import sentence_transformers
        import torch
        import transformers

        assert True
    except ImportError as e:
        pytest.fail(f"Falha ao importar dependências: {e!s}") 