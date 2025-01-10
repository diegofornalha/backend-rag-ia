from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os
import logging

logger = logging.getLogger(__name__)

class RenderMetrics:
    """Gerenciador de métricas integrado com dashboard do Render"""
    
    def __init__(self):
        self.metrics_path = os.getenv("RENDER_METRICS_PATH", "/metrics")
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Inicializa métricas padrão"""
        self._default_metrics = {
            # Métricas de performance
            "embate_response_time": {
                "type": "histogram",
                "description": "Tempo de resposta dos embates",
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            "embate_tokens_used": {
                "type": "counter",
                "description": "Total de tokens utilizados"
            },
            "embate_success_total": {
                "type": "counter",
                "description": "Total de embates bem-sucedidos"
            },
            "embate_failure_total": {
                "type": "counter",
                "description": "Total de embates com falha"
            },
            
            # Métricas de taxa
            "embate_success_rate": {
                "type": "gauge",
                "description": "Taxa de sucesso dos embates"
            },
            "embate_calls_per_minute": {
                "type": "gauge",
                "description": "Chamadas por minuto"
            },
            
            # Métricas de recursos
            "system_memory_usage": {
                "type": "gauge",
                "description": "Uso de memória do sistema"
            },
            "system_cpu_usage": {
                "type": "gauge",
                "description": "Uso de CPU do sistema"
            },
            
            # Métricas de cache
            "cache_hit_total": {
                "type": "counter",
                "description": "Total de cache hits"
            },
            "cache_miss_total": {
                "type": "counter",
                "description": "Total de cache misses"
            },
            "cache_hit_ratio": {
                "type": "gauge",
                "description": "Taxa de acerto do cache"
            },
            
            # Métricas de latência
            "strategy_latency": {
                "type": "histogram",
                "description": "Latência por estratégia",
                "buckets": [0.01, 0.05, 0.1, 0.5, 1.0]
            },
            
            # Métricas de saúde
            "system_health_status": {
                "type": "gauge",
                "description": "Status de saúde do sistema"
            },
            "health_check_failures": {
                "type": "counter",
                "description": "Falhas nos health checks"
            }
        }
        
    async def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ):
        """Registra uma métrica genérica"""
        if name not in self._default_metrics:
            logger.warning(f"Métrica não registrada: {name}")
            return
            
        metric_data = {
            "name": name,
            "value": value,
            "type": self._default_metrics[name]["type"],
            "timestamp": (timestamp or datetime.utcnow()).isoformat(),
            "labels": labels or {}
        }
        
        self._write_metric(metric_data)
        
    async def record_histogram(
        self,
        name: str,
        value: float,
        buckets: Optional[List[float]] = None,
        labels: Optional[Dict[str, str]] = None
    ):
        """Registra uma métrica do tipo histogram"""
        if name not in self._default_metrics or self._default_metrics[name]["type"] != "histogram":
            logger.warning(f"Histogram não registrado: {name}")
            return
            
        metric_data = {
            "name": f"{name}_histogram",
            "type": "histogram",
            "value": value,
            "buckets": buckets or self._default_metrics[name].get("buckets", []),
            "timestamp": datetime.utcnow().isoformat(),
            "labels": labels or {}
        }
        
        self._write_metric(metric_data)
        
    async def record_counter(
        self,
        name: str,
        increment: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """Registra uma métrica do tipo counter"""
        if name not in self._default_metrics or self._default_metrics[name]["type"] != "counter":
            logger.warning(f"Counter não registrado: {name}")
            return
            
        metric_data = {
            "name": f"{name}_total",
            "type": "counter",
            "value": increment,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": labels or {}
        }
        
        self._write_metric(metric_data)
        
    async def record_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """Registra uma métrica do tipo gauge"""
        if name not in self._default_metrics or self._default_metrics[name]["type"] != "gauge":
            logger.warning(f"Gauge não registrado: {name}")
            return
            
        metric_data = {
            "name": name,
            "type": "gauge",
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "labels": labels or {}
        }
        
        self._write_metric(metric_data)
        
    def _write_metric(self, metric_data: Dict[str, Any]):
        """Escreve a métrica no formato adequado para coleta do Render"""
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
            
            # Adiciona descrição da métrica
            metric_data["description"] = self._default_metrics[
                metric_data["name"].replace("_total", "").replace("_histogram", "")
            ]["description"]
            
            existing_metrics.append(metric_data)
            
            with open(metrics_file, "w") as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao registrar métrica: {e}")
            
    def get_metric_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Retorna informações sobre uma métrica específica"""
        return self._default_metrics.get(name)
        
    def list_available_metrics(self) -> List[Dict[str, Any]]:
        """Lista todas as métricas disponíveis com suas descrições"""
        return [
            {
                "name": name,
                "type": info["type"],
                "description": info["description"]
            }
            for name, info in self._default_metrics.items()
        ] 