"""
Interfaces base para os agentes do sistema.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AgentContext:
    """Contexto de execução do agente."""

    task: str
    data: dict[str, Any]
    metadata: dict[str, Any]


@dataclass
class AgentResponse:
    """Resposta de um agente após processamento."""

    agent: str
    status: str
    result: str | None = None
    error: str | None = None


@dataclass
class AgentResult:
    """Resultado da execução do agente."""

    success: bool
    findings: dict[str, Any]
    metadata: dict[str, Any]
    recommendations: list[str] | None = None
    errors: list[str] | None = None


class Agent(ABC):
    """Interface base para todos os agentes."""

    @abstractmethod
    async def process(self, task: str, context: dict[str, Any] | None = None) -> AgentResponse:
        """
        Processa uma tarefa.

        Args:
            task: Descrição da tarefa
            context: Contexto opcional

        Returns:
            Resultado do processamento
        """
        pass


class BaseAgent(ABC):
    """Interface base para todos os agentes."""

    @abstractmethod
    async def process(self, context: AgentContext) -> AgentResult:
        """
        Processa uma tarefa.

        Args:
            context: Contexto da tarefa

        Returns:
            Resultado do processamento
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Retorna as capacidades do agente.

        Returns:
            Lista de capacidades
        """
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Retorna o status atual do agente.

        Returns:
            Status do agente
        """
        pass


class TaskAgent(BaseAgent):
    """Agente base para processamento de tarefas."""

    def __init__(self):
        """Inicializa o agente."""
        self.tasks_processed = 0
        self.errors = 0

    async def process(self, context: AgentContext) -> AgentResult:
        """
        Processa uma tarefa específica.

        Args:
            context: Contexto da tarefa

        Returns:
            Resultado do processamento
        """
        try:
            result = await self._process_task(context)
            self.tasks_processed += 1
            return result
        except Exception as e:
            self.errors += 1
            return AgentResult(
                success=False, findings={}, metadata={"error": str(e)}, errors=[str(e)]
            )

    @abstractmethod
    async def _process_task(self, context: AgentContext) -> AgentResult:
        """
        Implementação específica do processamento.

        Args:
            context: Contexto da tarefa

        Returns:
            Resultado do processamento
        """
        pass

    def get_status(self) -> dict[str, Any]:
        """Retorna o status do agente."""
        return {
            "tasks_processed": self.tasks_processed,
            "errors": self.errors,
            "success_rate": (
                (self.tasks_processed - self.errors) / self.tasks_processed
                if self.tasks_processed > 0
                else 0
            ),
        }
