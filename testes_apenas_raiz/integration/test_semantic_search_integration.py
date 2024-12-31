import pytest
import requests

def test_semantic_search_endpoint():
    """Teste de integração para o endpoint de busca semântica."""
    base_url = "http://localhost:10000"
    query = "Como funciona a busca semântica?"
    
    try:
        response = requests.post(f"{base_url}/search", json={"query": query})
        assert response.status_code == 200
        assert "results" in response.json()
    except requests.exceptions.ConnectionError:
        pytest.skip("Servidor local não está rodando") 