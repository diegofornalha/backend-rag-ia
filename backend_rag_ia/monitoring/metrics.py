"""Módulo para coleta e agregação de métricas do sistema."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MetricValue:
    """Define um valor de métrica com metadados.
    
    Attributes
    ----------
    value : float | int
        Valor da métrica.
    timestamp : datetime
        Momento em que a métrica foi registrada.
    metadata : dict[str, Any] | None
        Metadados adicionais da métrica.
    """

    value: float | int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] | None = None


class MetricCollector:
    """Coleta e armazena métricas do sistema."""

    def __init__(self) -> None:
        self._metrics: dict[str, list[MetricValue]] = {}

    def record(self, name: str, value: float | int, metadata: dict[str, Any] | None = None) -> None:
        """Registra um novo valor para uma métrica."""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(MetricValue(value, metadata=metadata))

    def get_metric(self, name: str) -> list[MetricValue] | None:
        """Retorna todos os valores de uma métrica."""
        return self._metrics.get(name)

    def get_latest(self, name: str) -> MetricValue | None:
        """Retorna o valor mais recente de uma métrica."""
        values = self._metrics.get(name, [])
        return values[-1] if values else None

    def clear(self, name: str | None = None) -> None:
        """Limpa os valores de uma ou todas as métricas."""
        if name:
            self._metrics.pop(name, None)
        else:
            self._metrics.clear()


class MetricAggregator:
    """Agrega valores de métricas."""

    def __init__(self, collector: MetricCollector) -> None:
        self.collector = collector

    def average(self, name: str) -> float | None:
        """Calcula a média dos valores de uma métrica."""
        values = self.collector.get_metric(name)
        if not values:
            return None
        return sum(v.value for v in values) / len(values)

    def sum(self, name: str) -> float | None:
        """Calcula a soma dos valores de uma métrica."""
        values = self.collector.get_metric(name)
        if not values:
            return None
        return sum(v.value for v in values)

    def count(self, name: str) -> int:
        """Conta quantos valores uma métrica possui."""
        values = self.collector.get_metric(name)
        return len(values) if values else 0
