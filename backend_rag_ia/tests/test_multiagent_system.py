"""
Testes para o sistema multiagente.
"""

import pytest
from ..services.multiagent_system import MultiAgentSystem

@pytest.mark.asyncio
async def test_multiagent_basic_functionality():
    """Testa as funcionalidades básicas do sistema multiagente."""
    
    # Inicializa sistema
    system = MultiAgentSystem()
    
    # Verifica status inicial
    status = system.get_system_status()
    assert "coordinator" in status
    assert "tracker" in status
    assert "config" in status
    
    # Testa processamento de tarefa
    task_result = await system.process_task(
        "Analise o seguinte código: def soma(a, b): return a + b"
    )
    assert task_result is not None
    
    # Testa geração de resposta
    response = await system.generate_response(
        "Como posso melhorar este código?"
    )
    assert response is not None

@pytest.mark.asyncio
async def test_multiagent_error_handling():
    """Testa o tratamento de erros do sistema multiagente."""
    
    system = MultiAgentSystem()
    
    # Testa erro com tarefa inválida
    with pytest.raises(Exception):
        await system.process_task(None)
    
    # Testa erro com prompt inválido
    with pytest.raises(Exception):
        await system.generate_response(None) 