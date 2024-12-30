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

def test_torch_cuda():
    """Teste para verificar se o PyTorch está instalado corretamente"""
    import torch
    assert torch.__version__ is not None

def test_transformers():
    """Teste para verificar se o Transformers está instalado corretamente"""
    import transformers
    assert transformers.__version__ is not None

def test_sentence_transformers():
    """Teste para verificar se o Sentence Transformers está instalado corretamente"""
    import sentence_transformers
    assert sentence_transformers.__version__ is not None 