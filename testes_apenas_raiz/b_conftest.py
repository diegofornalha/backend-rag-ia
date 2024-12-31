import pytest
import json
import os

@pytest.fixture
def test_data():
    """Carrega dados de teste do arquivo JSON."""
    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures", "test_data.json")
    with open(fixtures_path) as f:
        return json.load(f)

@pytest.fixture
def api_base_url():
    """Retorna a URL base da API."""
    return os.getenv("API_BASE_URL", "http://localhost:10000") 