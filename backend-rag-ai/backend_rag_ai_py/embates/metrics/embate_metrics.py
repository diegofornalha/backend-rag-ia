from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class EmbateMetrics:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    timestamps: List[datetime] = field(default_factory=list)

class MetricsService:
    def __init__(self):
        self._metrics: Dict[str, EmbateMetrics] = {}
        
    def get_metrics(self, embate_id: str) -> EmbateMetrics:
        """Recupera métricas de um embate específico"""
        if embate_id not in self._metrics:
            self._metrics[embate_id] = EmbateMetrics()
        return self._metrics[embate_id]
        
    def record_call(self, embate_id: str, success: bool, response_time: float, tokens_used: int):
        """Registra uma chamada do embate"""
        metrics = self.get_metrics(embate_id)
        
        metrics.total_calls += 1
        metrics.timestamps.append(datetime.utcnow())
        
        if success:
            metrics.successful_calls += 1
        else:
            metrics.failed_calls += 1
            
        # Atualiza média de tempo de resposta
        metrics.average_response_time = (
            (metrics.average_response_time * (metrics.total_calls - 1) + response_time)
            / metrics.total_calls
        )
        
        metrics.total_tokens_used += tokens_used
        
    def get_success_rate(self, embate_id: str) -> float:
        """Calcula a taxa de sucesso do embate"""
        metrics = self.get_metrics(embate_id)
        if metrics.total_calls == 0:
            return 0.0
        return metrics.successful_calls / metrics.total_calls
        
    def get_calls_per_minute(self, embate_id: str) -> float:
        """Calcula a média de chamadas por minuto"""
        metrics = self.get_metrics(embate_id)
        if not metrics.timestamps:
            return 0.0
            
        time_span = (metrics.timestamps[-1] - metrics.timestamps[0]).total_seconds() / 60
        if time_span == 0:
            return float(metrics.total_calls)
            
        return metrics.total_calls / time_span 