"""
Sistema de eventos para embates.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class EmbateEvent:
    """Representa um evento do sistema de embates."""

    def __init__(self, tipo: str, dados: Dict[str, Any], timestamp: Optional[datetime] = None):
        """
        Inicializa o evento.

        Args:
            tipo: Tipo do evento
            dados: Dados do evento
            timestamp: Timestamp opcional do evento
        """
        self.tipo = tipo
        self.dados = dados
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Converte o evento para dicionário."""
        return {"tipo": self.tipo, "dados": self.dados, "timestamp": self.timestamp.isoformat()}


class EmbateEventManager:
    """Gerencia eventos do sistema de embates."""

    def __init__(self):
        """Inicializa o gerenciador de eventos."""
        self.handlers: Dict[str, List[Callable]] = {}
        self.eventos: List[EmbateEvent] = []

    def register_handler(self, tipo: str, handler: Callable) -> None:
        """
        Registra um handler para um tipo de evento.

        Args:
            tipo: Tipo do evento
            handler: Função que trata o evento
        """
        if tipo not in self.handlers:
            self.handlers[tipo] = []
        self.handlers[tipo].append(handler)

    def unregister_handler(self, tipo: str, handler: Callable) -> None:
        """
        Remove um handler de um tipo de evento.

        Args:
            tipo: Tipo do evento
            handler: Handler a remover
        """
        if tipo in self.handlers:
            self.handlers[tipo].remove(handler)
            if not self.handlers[tipo]:
                del self.handlers[tipo]

    async def dispatch(self, evento: EmbateEvent) -> None:
        """
        Dispara um evento para seus handlers.

        Args:
            evento: Evento a disparar
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

    def get_eventos(
        self,
        tipo: Optional[str] = None,
        inicio: Optional[datetime] = None,
        fim: Optional[datetime] = None,
    ) -> List[EmbateEvent]:
        """
        Retorna eventos filtrados.

        Args:
            tipo: Tipo opcional para filtrar
            inicio: Data inicial opcional
            fim: Data final opcional

        Returns:
            Lista de eventos filtrados
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
        """Limpa lista de eventos."""
        self.eventos = []

    def export_eventos(self) -> List[Dict[str, Any]]:
        """
        Exporta eventos como dicionários.

        Returns:
            Lista de eventos como dicionários
        """
        return [e.to_dict() for e in self.eventos]


class HallucinationEvent(EmbateEvent):
    """Evento específico para detecção de alucinações."""

    def __init__(
        self, embate_id: str, indicators: Dict[str, Any], timestamp: Optional[datetime] = None
    ):
        """
        Inicializa o evento de alucinação.

        Args:
            embate_id: ID do embate onde foi detectada alucinação
            indicators: Indicadores de alucinação
            timestamp: Timestamp opcional do evento
        """
        super().__init__(
            tipo="hallucination_detected",
            dados={"embate_id": embate_id, "indicators": indicators},
            timestamp=timestamp,
        )

    @property
    def score(self) -> float:
        """Retorna o score de alucinação."""
        return self.dados["indicators"]["score"]

    @property
    def is_severe(self) -> bool:
        """Indica se é uma alucinação severa."""
        return self.score > 0.8
