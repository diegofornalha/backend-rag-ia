from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class WorkflowMetrics:
    def __init__(self):
        self.metrics = defaultdict(int)
        self.timestamps = {}
        self.state_changes = defaultdict(list)

    def record_state_change(self, embate_id: str, old_state: str, new_state: str) -> None:
        """Registra mudança de estado"""
        self.metrics[f"state_change_{old_state}_to_{new_state}"] += 1

        timestamp = datetime.now()
        self.state_changes[embate_id].append(
            {"from": old_state, "to": new_state, "timestamp": timestamp}
        )

        logger.info(
            f"Estado do embate {embate_id} alterado de {old_state} "
            f"para {new_state} em {timestamp}"
        )

    def record_operation(self, embate_id: str, operation: str) -> None:
        """Registra uma operação"""
        self.metrics[f"operation_{operation}"] += 1
        timestamp = datetime.now()

        if embate_id not in self.timestamps:
            self.timestamps[embate_id] = {}

        self.timestamps[embate_id][operation] = timestamp

        logger.info(f"Operação {operation} registrada para embate {embate_id} " f"em {timestamp}")

    def get_cycle_time(self, embate_id: str) -> Optional[timedelta]:
        """Calcula tempo de ciclo de um embate"""
        if embate_id not in self.state_changes:
            return None

        changes = self.state_changes[embate_id]
        if not changes:
            return None

        first_event = changes[0]["timestamp"]
        last_event = changes[-1]["timestamp"]

        return last_event - first_event

    def get_state_duration(self, embate_id: str, state: str) -> timedelta:
        """Calcula duração total em um estado específico"""
        if embate_id not in self.state_changes:
            return timedelta()

        total_duration = timedelta()
        changes = self.state_changes[embate_id]

        for i in range(len(changes)):
            if changes[i]["to"] == state:
                start = changes[i]["timestamp"]
                # Se é o último estado, usa now()
                if i == len(changes) - 1:
                    end = datetime.now()
                else:
                    end = changes[i + 1]["timestamp"]
                total_duration += end - start

        return total_duration

    def get_statistics(self) -> Dict:
        """Retorna estatísticas gerais"""
        stats = {
            "total_embates": len(self.timestamps),
            "operations": dict(self.metrics),
            "state_changes": len(self.state_changes),
            "avg_cycle_time": self._calculate_avg_cycle_time(),
            "state_distribution": self._calculate_state_distribution(),
        }

        logger.info(f"Estatísticas geradas: {stats}")
        return stats

    def _calculate_avg_cycle_time(self) -> Optional[float]:
        """Calcula tempo médio de ciclo"""
        cycle_times = [self.get_cycle_time(embate_id) for embate_id in self.state_changes.keys()]

        valid_times = [ct for ct in cycle_times if ct is not None]
        if not valid_times:
            return None

        total_seconds = sum(ct.total_seconds() for ct in valid_times)
        return total_seconds / len(valid_times)

    def _calculate_state_distribution(self) -> Dict[str, int]:
        """Calcula distribuição de estados"""
        distribution = defaultdict(int)

        for changes in self.state_changes.values():
            if changes:  # Usa o último estado
                distribution[changes[-1]["to"]] += 1

        return dict(distribution)

    def clear(self) -> None:
        """Limpa todas as métricas"""
        self.metrics.clear()
        self.timestamps.clear()
        self.state_changes.clear()
        logger.info("Métricas limpas")
