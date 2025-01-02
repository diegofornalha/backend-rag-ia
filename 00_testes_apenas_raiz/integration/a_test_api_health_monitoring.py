from datetime import datetime

import pytest
import requests


def test_api_health():
    """Teste de monitoramento para verificar a saúde da API."""
    base_url = "http://localhost:10000"
    
    try:
        start_time = datetime.now()
        response = requests.get(f"{base_url}/health")
        response_time = (datetime.now() - start_time).total_seconds()
        
        assert response.status_code == 200
        assert response_time < 1.0  # Resposta deve ser menor que 1 segundo
        assert response.json()["status"] == "healthy"
    except requests.exceptions.ConnectionError:
        pytest.skip("Servidor local não está rodando") 