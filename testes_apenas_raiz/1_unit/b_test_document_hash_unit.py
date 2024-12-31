import pytest
from hashlib import sha256

def test_document_hash_generation():
    """Teste unitário para geração de hash de documento."""
    content = "Teste de conteúdo"
    expected_hash = sha256(content.encode()).hexdigest()
    assert len(expected_hash) == 64
    assert isinstance(expected_hash, str) 