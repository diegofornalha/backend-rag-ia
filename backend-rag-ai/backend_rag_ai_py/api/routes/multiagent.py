"""
Rotas para o sistema multi-agente.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from backend_rag_ai_py.services.agent_services.coordinator import AgentCoordinator
from backend_rag_ai_py.services.llm_services.providers.gemini import GeminiProvider

router = APIRouter()


def get_coordinator():
    """Retorna uma instância do coordenador de agentes."""
    try:
        provider = GeminiProvider()
        return AgentCoordinator(provider=provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inicializar coordenador: {str(e)}")


@router.post("/process")
async def process_task(
    task: dict[str, Any],
    coordinator: AgentCoordinator = Depends(get_coordinator),
):
    """
    Processa uma tarefa usando o sistema multi-agente.

    Args:
        task: Tarefa a ser processada
        coordinator: Coordenador de agentes

    Returns:
        dict: Resultado do processamento
    """
    try:
        result = await coordinator.process(task)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}") 