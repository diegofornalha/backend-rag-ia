"""Implementa sistema de métricas.

Este módulo fornece classes e funções para coletar, armazenar
e agregar métricas do sistema.
"""

from dataclasses import dataclass
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
    timestamp: datetime = datetime.now()
    metadata: dict[str, Any] | None = None


class MetricCollector:
    """Coleta e armazena métricas do sistema.

    Esta classe fornece métodos para registrar e recuperar
    valores de métricas ao longo do tempo.

    """

    def __init__(self) -> None:
        """Inicializa o coletor de métricas."""
        self._metrics: dict[str, list[MetricValue]] = {}

    def record(self, name: str, value: float | int, metadata: dict[str, Any] | None = None) -> None:
        """Registra um novo valor de métrica.

        Parameters
        ----------
        name : str
            Nome da métrica.
        value : float | int
            Valor a ser registrado.
        metadata : dict[str, Any] | None, optional
            Metadados adicionais, por padrão None.

        """
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(MetricValue(value, metadata=metadata))

    def get_metric(self, name: str) -> list[MetricValue] | None:
        """Retorna todos os valores de uma métrica.

        Parameters
        ----------
        name : str
            Nome da métrica.

        Returns
        -------
        list[MetricValue] | None
            Lista de valores ou None se a métrica não existe.

        """
        return self._metrics.get(name)

    def get_latest(self, name: str) -> MetricValue | None:
        """Retorna o valor mais recente de uma métrica.

        Parameters
        ----------
        name : str
            Nome da métrica.

        Returns
        -------
        MetricValue | None
            Valor mais recente ou None se a métrica não existe.

        """
        values = self._metrics.get(name, [])
        return values[-1] if values else None

    def clear(self, name: str | None = None) -> None:
        """Remove métricas do coletor.

        Parameters
        ----------
        name : str | None, optional
            Nome da métrica a remover, por padrão None.
            Se None, remove todas as métricas.

        """
        if name:
            self._metrics.pop(name, None)
        else:
            self._metrics.clear()


class MetricAggregator:
    """Agrega valores de métricas.

    Esta classe fornece métodos para calcular agregações
    como média, soma e contagem de valores de métricas.

    """

    def __init__(self, collector: MetricCollector) -> None:
        """Inicializa o agregador de métricas.

        Parameters
        ----------
        collector : MetricCollector
            Coletor de métricas a ser usado.

        """
        self.collector = collector

    def average(self, name: str) -> float | None:
        """Calcula a média dos valores de uma métrica.

        Parameters
        ----------
        name : str
            Nome da métrica.

        Returns
        -------
        float | None
            Média dos valores ou None se a métrica não existe.

        """
        values = self.collector.get_metric(name)
        if not values:
            return None
        return sum(v.value for v in values) / len(values)

    def sum(self, name: str) -> float | None:
        """Calcula a soma dos valores de uma métrica.

        Parameters
        ----------
        name : str
            Nome da métrica.

        Returns
        -------
        float | None
            Soma dos valores ou None se a métrica não existe.

        """
        values = self.collector.get_metric(name)
        if not values:
            return None
        return sum(v.value for v in values)

    def count(self, name: str) -> int:
        """Conta quantos valores uma métrica possui.

        Parameters
        ----------
        name : str
            Nome da métrica.

        Returns
        -------
        int
            Número de valores registrados.

        """
        values = self.collector.get_metric(name)
        return len(values) if values else 0
