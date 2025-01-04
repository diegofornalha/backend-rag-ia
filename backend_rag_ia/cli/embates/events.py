"""Implementa sistema de eventos para embates.

Este módulo implementa um sistema de eventos para gerenciar e monitorar embates,
incluindo detecção de alucinações e outros eventos relevantes.
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any, Optional


class EmbateEvent:
    """Define um evento do sistema de embates.

    Esta classe fornece a estrutura básica para eventos no sistema,
    incluindo tipo, dados e timestamp.

    Attributes
    ----------
    tipo : str
        O tipo do evento.
    dados : dict[str, Any]
        Os dados associados ao evento.
    timestamp : datetime
        O momento em que o evento ocorreu.

    """

    def __init__(self,
                 tipo: str,
                 dados: dict[str, Any],
                 timestamp: Optional[datetime] = None):
        """Inicializa um novo evento do sistema.

        Parameters
        ----------
        tipo : str
            O tipo do evento.
        dados : dict[str, Any]
            Os dados associados ao evento.
        timestamp : Optional[datetime], optional
            O momento em que o evento ocorreu, por padrão None.

        """
        self.tipo = tipo
        self.dados = dados
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Retorna o evento como um dicionário.

        Returns
        -------
        dict[str, Any]
            O evento convertido em formato de dicionário.

        """
        return {
            "tipo": self.tipo,
            "dados": self.dados,
            "timestamp": self.timestamp.isoformat()
        }


class EmbateEventManager:
    """Gerencia eventos do sistema de embates.

    Esta classe é responsável por registrar, despachar e gerenciar
    eventos do sistema de embates.

    Attributes
    ----------
    handlers : dict[str, list[Callable]]
        Dicionário de handlers registrados por tipo de evento.
    eventos : list[EmbateEvent]
        Lista de eventos registrados no sistema.

    """

    def __init__(self):
        """Inicializa o gerenciador de eventos."""
        self.handlers: dict[str, list[Callable]] = {}
        self.eventos: list[EmbateEvent] = []

    def register_handler(self, tipo: str, handler: Callable) -> None:
        """Registra um handler para um tipo de evento.

        Parameters
        ----------
        tipo : str
            O tipo do evento a ser monitorado.
        handler : Callable
            A função que tratará o evento.

        """
        if tipo not in self.handlers:
            self.handlers[tipo] = []
        self.handlers[tipo].append(handler)

    def unregister_handler(self, tipo: str, handler: Callable) -> None:
        """Remove um handler de um tipo de evento.

        Parameters
        ----------
        tipo : str
            O tipo do evento.
        handler : Callable
            O handler a ser removido.

        """
        if tipo in self.handlers:
            self.handlers[tipo].remove(handler)
            if not self.handlers[tipo]:
                del self.handlers[tipo]

    async def dispatch(self, evento: EmbateEvent) -> None:
        """Dispara um evento para seus handlers registrados.

        Parameters
        ----------
        evento : EmbateEvent
            O evento a ser disparado.

        """
        # Registra evento
        self.eventos.append(evento)

        # Chama handlers
        if evento.tipo in self.handlers:
            for handler in self.handlers[evento.tipo]:
                try:
                    await handler(evento)
                except Exception as e:
                    print(f"Erro ao processar evento: {e}")

    def get_eventos(self,
                   tipo: Optional[str] = None,
                   inicio: Optional[datetime] = None,
                   fim: Optional[datetime] = None) -> list[EmbateEvent]:
        """Retorna eventos filtrados por critérios específicos.

        Parameters
        ----------
        tipo : Optional[str], optional
            O tipo de evento para filtrar, por padrão None.
        inicio : Optional[datetime], optional
            A data inicial do período, por padrão None.
        fim : Optional[datetime], optional
            A data final do período, por padrão None.

        Returns
        -------
        list[EmbateEvent]
            Lista de eventos que atendem aos critérios de filtragem.

        """
        eventos = self.eventos

        if tipo:
            eventos = [e for e in eventos if e.tipo == tipo]

        if inicio:
            eventos = [e for e in eventos if e.timestamp >= inicio]

        if fim:
            eventos = [e for e in eventos if e.timestamp <= fim]

        return eventos

    def clear_eventos(self) -> None:
        """Remove todos os eventos registrados."""
        self.eventos = []

    def export_eventos(self) -> list[dict[str, Any]]:
        """Retorna todos os eventos como dicionários.

        Returns
        -------
        list[dict[str, Any]]
            Lista de eventos convertidos em formato de dicionário.

        """
        return [e.to_dict() for e in self.eventos]


class HallucinationEvent(EmbateEvent):
    """Define um evento específico para detecção de alucinações.

    Esta classe representa eventos relacionados à detecção de alucinações
    em embates, incluindo métricas e indicadores.

    Attributes
    ----------
    embate_id : str
        ID do embate onde foi detectada a alucinação.
    indicators : dict[str, Any]
        Indicadores e métricas da alucinação detectada.

    """

    def __init__(self,
                 embate_id: str,
                 indicators: dict[str, Any],
                 timestamp: Optional[datetime] = None):
        """Inicializa um novo evento de alucinação.

        Parameters
        ----------
        embate_id : str
            ID do embate onde foi detectada a alucinação.
        indicators : dict[str, Any]
            Indicadores e métricas da alucinação.
        timestamp : Optional[datetime], optional
            O momento da detecção, por padrão None.

        """
        super().__init__(
            tipo="hallucination_detected",
            dados={
                "embate_id": embate_id,
                "indicators": indicators
            },
            timestamp=timestamp
        )

    @property
    def score(self) -> float:
        """Retorna o score de alucinação.

        Returns
        -------
        float
            O score calculado para a alucinação.

        """
        return self.dados["indicators"]["score"]

    @property
    def is_severe(self) -> bool:
        """Indica se a alucinação é considerada severa.

        Returns
        -------
        bool
            True se o score for maior que 0.8, False caso contrário.

        """
        return self.score > 0.8
