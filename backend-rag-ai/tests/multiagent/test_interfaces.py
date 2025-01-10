"""
Testes para as interfaces dos agentes.
"""

import pytest
from backend_rag_ia.services.multiagent.core.interfaces import (
    AgentContext,
    AgentResult,
    TaskAgent
)

# Implementação de teste movida para função factory
def create_test_agent():
    """Cria um agente de teste."""
    class TestTaskAgent(TaskAgent):
        """Implementação de teste do TaskAgent."""
        
        async def _process_task(self, context: AgentContext) -> AgentResult:
            """Implementação de teste."""
            if context.task == "error":
                raise ValueError("Erro de teste")
                
            return AgentResult(
                success=True,
                findings={"test": "ok"},
                metadata={"processed": True}
            )
        
        def get_capabilities(self) -> list[str]:
            """Retorna capacidades de teste."""
            return ["test"]
    
    return TestTaskAgent()

@pytest.fixture
def agent():
    """Agente de teste."""
    return create_test_agent()

@pytest.mark.asyncio
async def test_successful_processing(agent):
    """Testa processamento bem sucedido."""
    context = AgentContext(
        task="test",
        data={},
        metadata={}
    )
    
    result = await agent.process(context)
    
    assert result.success is True
    assert result.findings == {"test": "ok"}
    assert result.metadata == {"processed": True}
    assert agent.tasks_processed == 1
    assert agent.errors == 0

@pytest.mark.asyncio
async def test_error_handling(agent):
    """Testa tratamento de erros."""
    context = AgentContext(
        task="error",
        data={},
        metadata={}
    )
    
    result = await agent.process(context)
    
    assert result.success is False
    assert result.errors == ["Erro de teste"]
    assert agent.tasks_processed == 0
    assert agent.errors == 1

def test_agent_status(agent):
    """Testa status do agente."""
    status = agent.get_status()
    
    assert "tasks_processed" in status
    assert "errors" in status
    assert "success_rate" in status
    assert status["success_rate"] == 0  # Nenhuma tarefa processada

def test_agent_capabilities(agent):
    """Testa capacidades do agente."""
    capabilities = agent.get_capabilities()
    
    assert isinstance(capabilities, list)
    assert "test" in capabilities 