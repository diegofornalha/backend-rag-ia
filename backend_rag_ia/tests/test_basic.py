import pytest


def test_environment():
    """Teste básico para verificar se o ambiente está funcionando"""
    try:
        import torch
        import transformers
        import sentence_transformers
        import faiss

        assert True
    except ImportError as e:
        pytest.fail(f"Falha ao importar dependências: {str(e)}")
