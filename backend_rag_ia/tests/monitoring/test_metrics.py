"""
Testes para o módulo de métricas.
"""

import pytest
from datetime import datetime

from ...monitoring.metrics import Metrica, MetricsCollector, MAX_TOOLS

def test_limite_ferramentas():
    """Testa se o limite de ferramentas está funcionando."""
    metrica = Metrica(
        nome="teste",
        valor=1.0,
        timestamp=datetime.now()
    )
    
    # Primeiras chamadas devem retornar True
    for i in range(MAX_TOOLS - 1):
        assert metrica.incrementar_tools() == True, f"Falhou na ferramenta {i+1}"
        
    # Última chamada deve retornar False e mostrar mensagem
    assert metrica.incrementar_tools() == False, "Deveria ter parado no limite"
    assert metrica.tools_count == MAX_TOOLS, f"Contador deveria ser {MAX_TOOLS}"

def test_collector_limite():
    """Testa se o coletor respeita o limite de ferramentas."""
    collector = MetricsCollector()
    
    # Registra métricas até o limite
    for i in range(MAX_TOOLS):
        if i < MAX_TOOLS - 1:
            collector.registrar(f"metrica_{i}", i)
        else:
            with pytest.raises(ValueError) as excinfo:
                collector.registrar(f"metrica_{i}", i)
            assert "Limite de 3 ferramentas atingido" in str(excinfo.value) 