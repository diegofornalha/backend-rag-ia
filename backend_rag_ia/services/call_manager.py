"""Módulo para gerenciamento de chamadas.

Este módulo fornece funcionalidades para gerenciar chamadas sequenciais
e paralelas, incluindo controle de concorrência e limites de taxa.
"""

from collections import deque
from datetime import datetime, timedelta
from typing import Any


class CallManager:
    """Gerenciador de chamadas.

    Esta classe fornece métodos para gerenciar chamadas sequenciais
    e paralelas, incluindo controle de concorrência e limites de taxa.

    Attributes
    ----------
    max_calls_per_minute : int
        Número máximo de chamadas permitidas por minuto.
    call_history : deque
        Histórico de chamadas realizadas.
    max_concurrent_calls : int
        Número máximo de chamadas concorrentes permitidas.
    active_calls : int
        Número atual de chamadas ativas.

    """

    def __init__(
        self,
        max_calls_per_minute: int = 60,
        max_concurrent_calls: int = 10
    ) -> None:
        """Inicializa o gerenciador.

        Parameters
        ----------
        max_calls_per_minute : int, optional
            Número máximo de chamadas por minuto, por padrão 60.
        max_concurrent_calls : int, optional
            Número máximo de chamadas concorrentes, por padrão 10.

        """
        self.max_calls_per_minute = max_calls_per_minute
        self.call_history = deque(maxlen=max_calls_per_minute)
        self.max_concurrent_calls = max_concurrent_calls
        self.active_calls = 0

    def can_make_call(self) -> bool:
        """Verifica se é possível fazer uma nova chamada.

        Returns
        -------
        bool
            True se uma nova chamada pode ser feita, False caso contrário.

        """
        # Remove chamadas antigas do histórico
        current_time = datetime.now()
        while (
            self.call_history and
            current_time - self.call_history[0] > timedelta(minutes=1)
        ):
            self.call_history.popleft()

        # Verifica limites
        return (
            len(self.call_history) < self.max_calls_per_minute and
            self.active_calls < self.max_concurrent_calls
        )

    def register_call(self) -> None:
        """Registra uma nova chamada.

        Atualiza o histórico de chamadas e o contador de chamadas ativas.
        """
        self.call_history.append(datetime.now())
        self.active_calls += 1

    def complete_call(self) -> None:
        """Marca uma chamada como concluída.

        Decrementa o contador de chamadas ativas.
        """
        if self.active_calls > 0:
            self.active_calls -= 1

    def get_stats(self) -> dict[str, Any]:
        """Obtém estatísticas do gerenciador.

        Returns
        -------
        dict[str, Any]
            Estatísticas atuais do gerenciador.

        """
        return {
            "active_calls": self.active_calls,
            "calls_in_last_minute": len(self.call_history),
            "max_calls_per_minute": self.max_calls_per_minute,
            "max_concurrent_calls": self.max_concurrent_calls
        }
