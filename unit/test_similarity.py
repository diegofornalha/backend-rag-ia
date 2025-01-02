"""Testes unitários para funções de similaridade."""

import numpy as np
import pytest

from backend_rag_ia.cli.c_embates_saudaveis import cosine_similarity


def test_cosine_similarity_identical():
    """Testa similaridade entre vetores idênticos."""
    v1 = [1, 0, 0, 1]
    v2 = [1, 0, 0, 1]
    assert cosine_similarity(v1, v2) == pytest.approx(1.0)

def test_cosine_similarity_orthogonal():
    """Testa similaridade entre vetores ortogonais."""
    v1 = [1, 0, 0]
    v2 = [0, 1, 0]
    assert cosine_similarity(v1, v2) == pytest.approx(0.0)

def test_cosine_similarity_opposite():
    """Testa similaridade entre vetores opostos."""
    v1 = [1, 1, 1]
    v2 = [-1, -1, -1]
    assert cosine_similarity(v1, v2) == pytest.approx(-1.0)

def test_cosine_similarity_similar():
    """Testa similaridade entre vetores semelhantes."""
    v1 = [1, 1, 0]
    v2 = [1, 0.8, 0.2]
    # Calcula o valor esperado manualmente
    expected = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    assert cosine_similarity(v1, v2) == pytest.approx(expected)

def test_cosine_similarity_zero_vector():
    """Testa similaridade com vetor zero."""
    v1 = [0, 0, 0]
    v2 = [1, 1, 1]
    with pytest.raises(ZeroDivisionError):
        cosine_similarity(v1, v2)

def test_cosine_similarity_different_dimensions():
    """Testa similaridade entre vetores de dimensões diferentes."""
    v1 = [1, 2, 3]
    v2 = [1, 2]
    with pytest.raises(ValueError):
        cosine_similarity(v1, v2)

def test_cosine_similarity_float_precision():
    """Testa precisão com números float."""
    v1 = [0.123456789, 0.987654321]
    v2 = [0.123456789, 0.987654321]
    assert cosine_similarity(v1, v2) == pytest.approx(1.0)

def test_cosine_similarity_large_vectors():
    """Testa similaridade com vetores grandes."""
    v1 = list(range(1000))
    v2 = list(range(1000))
    assert cosine_similarity(v1, v2) == pytest.approx(1.0)

def test_cosine_similarity_sparse_vectors():
    """Testa similaridade com vetores esparsos."""
    v1 = [1, 0, 0, 0, 1, 0, 0, 0, 1]
    v2 = [0, 0, 1, 0, 1, 0, 1, 0, 0]
    expected = 1/3  # Apenas uma posição em comum (índice 4)
    assert cosine_similarity(v1, v2) == pytest.approx(expected) 