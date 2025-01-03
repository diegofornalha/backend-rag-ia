"""
Monitoramento de qualidade de busca.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

@dataclass
class ResultadoBusca:
    """Modelo para resultados de busca."""
    query: str
    resultados: List[str]
    tempo_resposta: float
    timestamp: datetime
    feedback: Optional[str] = None

@dataclass
class LatencyMetric:
    """Métrica de latência."""
    p50: float = 0.0
    p90: float = 0.0
    p99: float = 0.0
    min: float = float("inf")
    max: float = 0.0
    amostras: List[float] = None
    
    def __post_init__(self):
        if self.amostras is None:
            self.amostras = []
            
    def adicionar_amostra(self, valor: float) -> None:
        """
        Adiciona uma amostra de latência.
        
        Args:
            valor: Valor da latência
        """
        self.amostras.append(valor)
        self.min = min(self.min, valor)
        self.max = max(self.max, valor)
        
        # Atualiza percentis
        if len(self.amostras) >= 2:
            amostras_ordenadas = sorted(self.amostras)
            n = len(amostras_ordenadas)
            
            self.p50 = amostras_ordenadas[n // 2]
            self.p90 = amostras_ordenadas[int(n * 0.9)]
            self.p99 = amostras_ordenadas[int(n * 0.99)]

class SearchQualityMonitor:
    """Monitor de qualidade de busca."""
    
    def __init__(self):
        self.buscas: List[ResultadoBusca] = []
        self.latency_metrics = LatencyMetric()
        
    def registrar_busca(self, 
                       query: str,
                       resultados: List[str],
                       tempo_resposta: float,
                       feedback: Optional[str] = None) -> None:
        """
        Registra uma busca realizada.
        
        Args:
            query: Query de busca
            resultados: Lista de resultados
            tempo_resposta: Tempo de resposta em segundos
            feedback: Feedback opcional do usuário
        """
        busca = ResultadoBusca(
            query=query,
            resultados=resultados,
            tempo_resposta=tempo_resposta,
            timestamp=datetime.now(),
            feedback=feedback
        )
        self.buscas.append(busca)
        self.latency_metrics.adicionar_amostra(tempo_resposta)
        
    def get_metricas(self) -> Dict:
        """
        Calcula métricas de qualidade.
        
        Returns:
            Métricas calculadas
        """
        if not self.buscas:
            return {
                "total_buscas": 0,
                "tempo_medio": 0.0,
                "taxa_feedback_positivo": 0.0,
                "queries_sem_resultado": 0,
                "latencia": {
                    "p50": 0.0,
                    "p90": 0.0,
                    "p99": 0.0,
                    "min": 0.0,
                    "max": 0.0
                }
            }
            
        total = len(self.buscas)
        tempo_medio = sum(b.tempo_resposta for b in self.buscas) / total
        
        buscas_com_feedback = [b for b in self.buscas if b.feedback]
        feedback_positivo = len([
            b for b in buscas_com_feedback
            if b.feedback.lower() in ["bom", "ótimo", "excelente"]
        ])
        
        taxa_feedback = (
            feedback_positivo / len(buscas_com_feedback)
            if buscas_com_feedback else 0.0
        )
        
        sem_resultado = len([b for b in self.buscas if not b.resultados])
        
        return {
            "total_buscas": total,
            "tempo_medio": tempo_medio,
            "taxa_feedback_positivo": taxa_feedback,
            "queries_sem_resultado": sem_resultado,
            "latencia": {
                "p50": self.latency_metrics.p50,
                "p90": self.latency_metrics.p90,
                "p99": self.latency_metrics.p99,
                "min": self.latency_metrics.min,
                "max": self.latency_metrics.max
            }
        }
        
    def get_queries_problematicas(self) -> List[str]:
        """
        Identifica queries problemáticas.
        
        Returns:
            Lista de queries com problemas
        """
        problematicas = []
        
        for busca in self.buscas:
            # Sem resultados
            if not busca.resultados:
                problematicas.append(f"Sem resultados: {busca.query}")
                
            # Tempo alto
            elif busca.tempo_resposta > 2.0:  # mais de 2 segundos
                problematicas.append(
                    f"Tempo alto ({busca.tempo_resposta:.1f}s): {busca.query}"
                )
                
            # Feedback negativo
            elif busca.feedback and busca.feedback.lower() in ["ruim", "péssimo"]:
                problematicas.append(f"Feedback negativo: {busca.query}")
                
        return problematicas 