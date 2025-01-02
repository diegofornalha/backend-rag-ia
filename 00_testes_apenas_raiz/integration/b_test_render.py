"""
Testes de renderização.
"""

import logging

import requests

logger = logging.getLogger(__name__)

def test_render() -> None:
    """Testa renderização."""
    # Arrange
    base_url = "http://localhost:3000"
    
    # Act
    response = requests.get(base_url)
    
    # Assert
    assert response.status_code == 200 