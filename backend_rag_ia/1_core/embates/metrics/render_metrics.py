from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
import os

class RenderMetrics:
    """Gerenciador de métricas integrado com dashboard do Render"""
    
    def __init__(self):
        self.metrics_path = os.getenv("RENDER_METRICS_PATH", "/metrics")
        
    async def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Registra uma métrica no formato do Render"""
        metric_data = {
            "name": name,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": labels or {}
        }
        
        # No ambiente Render, as métricas são coletadas automaticamente
        # do endpoint /metrics no formato Prometheus
        self._write_metric(metric_data)
        
    async def record_histogram(self, name: str, value: float, buckets: List[float] = None):
        """Registra uma métrica do tipo histogram"""
        if buckets is None:
            buckets = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            
        metric_data = {
            "name": f"{name}_histogram",
            "type": "histogram",
            "value": value,
            "buckets": buckets,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._write_metric(metric_data)
        
    async def record_counter(self, name: str, increment: float = 1.0):
        """Registra uma métrica do tipo counter"""
        metric_data = {
            "name": f"{name}_total",
            "type": "counter",
            "value": increment,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._write_metric(metric_data)
        
    async def record_gauge(self, name: str, value: float):
        """Registra uma métrica do tipo gauge"""
        metric_data = {
            "name": name,
            "type": "gauge",
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._write_metric(metric_data)
        
    def _write_metric(self, metric_data: Dict[str, Any]):
        """Escreve a métrica no formato adequado para coleta do Render"""
        # Em produção, o Render coleta métricas automaticamente
        # Esta implementação é para desenvolvimento local
        metrics_file = os.path.join(self.metrics_path, "metrics.json")
        
        try:
            existing_metrics = []
            if os.path.exists(metrics_file):
                with open(metrics_file, "r") as f:
                    existing_metrics = json.load(f)
                    
            # Remove métricas antigas (mais de 5 minutos)
            current_time = datetime.utcnow()
            existing_metrics = [
                m for m in existing_metrics
                if datetime.fromisoformat(m["timestamp"]) > current_time - timedelta(minutes=5)
            ]
            
            existing_metrics.append(metric_data)
            
            with open(metrics_file, "w") as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            # Em desenvolvimento, falhas no registro de métricas não devem
            # impactar o funcionamento do sistema
            print(f"Erro ao registrar métrica: {e}") 