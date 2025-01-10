import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EmbateMetric:
    timestamp: datetime
    embate_id: str
    operation: str
    duration_ms: float
    success: bool
    error_type: str | None = None
    details: dict | None = None


class EmbatesMetrics:
    def __init__(self, max_history: int = 1000):
        self.metrics: list[EmbateMetric] = []
        self.max_history = max_history

    def record_operation(self, metric: EmbateMetric) -> None:
        """Registra uma nova métrica"""
        self.metrics.append(metric)

        # Mantém o histórico limitado
        if len(self.metrics) > self.max_history:
            self.metrics = self.metrics[-self.max_history :]

        # Log da operação
        log_msg = (
            f"Operação registrada - Embate: {metric.embate_id}, "
            f"Operação: {metric.operation}, "
            f"Duração: {metric.duration_ms}ms, "
            f"Sucesso: {metric.success}"
        )

        if metric.error_type:
            log_msg += f", Erro: {metric.error_type}"

        logger.info(log_msg)

    def _calculate_success_rate(self) -> float:
        """Calcula taxa de sucesso"""
        if not self.metrics:
            return 0.0

        successful = sum(1 for m in self.metrics if m.success)
        return successful / len(self.metrics)

    def _calculate_avg_duration(self) -> float:
        """Calcula duração média"""
        if not self.metrics:
            return 0.0

        total_duration = sum(m.duration_ms for m in self.metrics)
        return total_duration / len(self.metrics)

    def _get_error_distribution(self) -> dict[str, int]:
        """Calcula distribuição de erros"""
        errors = defaultdict(int)
        for metric in self.metrics:
            if not metric.success and metric.error_type:
                errors[metric.error_type] += 1
        return dict(errors)

    def _get_operation_distribution(self) -> dict[str, int]:
        """Calcula distribuição de operações"""
        operations = defaultdict(int)
        for metric in self.metrics:
            operations[metric.operation] += 1
        return dict(operations)

    def get_statistics(self) -> dict:
        """Retorna estatísticas completas"""
        return {
            "total_operations": len(self.metrics),
            "success_rate": self._calculate_success_rate(),
            "avg_duration_ms": self._calculate_avg_duration(),
            "error_distribution": self._get_error_distribution(),
            "operation_distribution": self._get_operation_distribution(),
            "last_operation": self.metrics[-1] if self.metrics else None,
            "history_size": len(self.metrics),
            "max_history": self.max_history,
        }

    def get_metrics_by_embate(self, embate_id: str) -> list[EmbateMetric]:
        """Retorna métricas de um embate específico"""
        return [m for m in self.metrics if m.embate_id == embate_id]

    def clear(self) -> None:
        """Limpa todas as métricas"""
        self.metrics.clear()
        logger.info("Métricas limpas")
