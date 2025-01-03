"""Controle de limites para refatorações."""

from datetime import datetime
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from .refactoring_metrics import MetricsAnalyzer, SemanticAnalyzer, CodeMetrics
from .refactoring_observer import (
    RefactoringEvent,
    RefactoringSubject,
    ChatObserver,
    CodeObserver
)

class RefactoringLimitsChecker:
    """Controla limites e métricas de refatorações."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        
        # Sistema de observadores
        self.subject = RefactoringSubject()
        self.chat_observer = ChatObserver()
        self.code_observer = CodeObserver()
        
        self.subject.attach(self.chat_observer)
        self.subject.attach(self.code_observer)
        
        # Analisadores
        self.metrics_analyzer = MetricsAnalyzer()
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Estado
        self.history: List[Dict] = []
        self.history_file = self.project_root / "refactoring_history.json"
        self.thresholds = self._load_thresholds()
        self.current_metrics: Optional[CodeMetrics] = None
        self.file_metrics: Dict[str, CodeMetrics] = {}
        
    def _load_thresholds(self) -> Dict:
        """Carrega thresholds de configuração."""
        config_file = self.project_root / "refactoring_config.json"
        
        default_thresholds = {
            "max_iterations": 5,
            "min_impact_per_change": 0.2,
            "max_consolidated_ratio": 0.8,
            "diminishing_returns_threshold": 0.3,
            "max_complexity": 15,
            "min_cohesion": 0.5,
            "max_coupling": 0.7,
            "max_dependencies": 20
        }
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    custom_thresholds = json.load(f)
                default_thresholds.update(custom_thresholds)
            except Exception as e:
                self.logger.warning(f"Erro ao carregar configurações: {e}")
                
        return default_thresholds
    
    def process_event(self, event_type: str, content: str, metrics: Optional[Dict] = None) -> Dict:
        """Processa um evento de refatoração."""
        event = RefactoringEvent(
            timestamp=datetime.now(),
            type=event_type,
            content=content,
            metrics=metrics or {}
        )
        self.subject.notify(event)
        
        analysis = self.subject.get_analysis()
        
        # Verifica desvios de propósito
        if analysis["deviations"]["purpose"]:
            return {
                "continue": False,
                "reason": "Detectado desvio do propósito original"
            }
            
        # Verifica métricas de código se for evento de código
        if event_type == 'code' and metrics and 'file_path' in metrics:
            file_metrics = self.metrics_analyzer.analyze_file(Path(metrics['file_path']))
            self.file_metrics[metrics['file_path']] = file_metrics
            
            if not self._check_code_metrics(file_metrics):
                return {
                    "continue": False,
                    "reason": self._get_metrics_violation_reason(file_metrics)
                }
            
            # Analisa mudanças semânticas se houver versão anterior
            if 'old_content' in metrics and 'new_content' in metrics:
                semantic_changes = self.semantic_analyzer.analyze_changes(
                    metrics['old_content'],
                    metrics['new_content']
                )
                
                if not self._check_semantic_changes(semantic_changes):
                    return {
                        "continue": False,
                        "reason": self._get_semantic_violation_reason(semantic_changes)
                    }
        
        return self.should_continue_refactoring(analysis["metrics"])
    
    def should_continue_refactoring(self, current_metrics: Dict) -> Dict[str, bool]:
        """Avalia se deve continuar com as refatorações."""
        if not self.history:
            self.history.append(current_metrics)
            self._save_history()
            return {"continue": True, "reason": "Primeira iteração"}
            
        previous = self.history[-1]
        
        # Verifica consolidação excessiva primeiro
        consolidated_ratio = current_metrics["consolidated"] / \
                           max(current_metrics["total_changes"], 1)
        if consolidated_ratio > self.thresholds["max_consolidated_ratio"]:
            return {
                "continue": False,
                "reason": "Muita consolidação, possível over-engineering"
            }
            
        # Verifica retornos diminutos se houver histórico suficiente
        if len(self.history) >= 3:
            trend = self._calculate_improvement_trend()
            if trend < self.thresholds["diminishing_returns_threshold"]:
                return {
                    "continue": False,
                    "reason": "Retornos diminutos detectados"
                }
                
        # Verifica número de iterações por último
        if current_metrics["iterations"] >= self.thresholds["max_iterations"]:
            return {
                "continue": False,
                "reason": "Atingido limite máximo de iterações"
            }
        
        self.history.append(current_metrics)
        self._save_history()
        return {"continue": True, "reason": "Melhorias ainda são significativas"}
    
    def _check_code_metrics(self, metrics: CodeMetrics) -> bool:
        """Verifica se métricas de código estão dentro dos limites."""
        return (
            metrics.cyclomatic_complexity <= self.thresholds["max_complexity"] and
            metrics.module_cohesion >= self.thresholds["min_cohesion"] and
            metrics.coupling_score <= self.thresholds["max_coupling"] and
            len(metrics.dependencies) <= self.thresholds["max_dependencies"]
        )
    
    def _check_semantic_changes(self, changes: Dict) -> bool:
        """Verifica se mudanças semânticas são aceitáveis."""
        complexity_changes = changes["complexity_changes"]
        api_changes = changes["api_changes"]
        
        # Verifica se complexidade não aumentou muito
        if complexity_changes["complexity_delta"] > 5:  # Limite arbitrário
            return False
            
        # Verifica se não há muitas breaking changes
        if len(api_changes["breaking_changes"]) > 2:  # Limite arbitrário
            return False
            
        return True
    
    def _get_metrics_violation_reason(self, metrics: CodeMetrics) -> str:
        """Retorna razão da violação de métricas."""
        reasons = []
        
        if metrics.cyclomatic_complexity > self.thresholds["max_complexity"]:
            reasons.append(f"Complexidade muito alta ({metrics.cyclomatic_complexity})")
            
        if metrics.module_cohesion < self.thresholds["min_cohesion"]:
            reasons.append(f"Coesão muito baixa ({metrics.module_cohesion:.2f})")
            
        if metrics.coupling_score > self.thresholds["max_coupling"]:
            reasons.append(f"Acoplamento muito alto ({metrics.coupling_score:.2f})")
            
        if len(metrics.dependencies) > self.thresholds["max_dependencies"]:
            reasons.append(f"Muitas dependências ({len(metrics.dependencies)})")
            
        return " | ".join(reasons)
    
    def _get_semantic_violation_reason(self, changes: Dict) -> str:
        """Retorna razão da violação semântica."""
        reasons = []
        
        complexity_delta = changes["complexity_changes"]["complexity_delta"]
        if complexity_delta > 5:
            reasons.append(f"Aumento significativo de complexidade (+{complexity_delta})")
            
        breaking_changes = len(changes["api_changes"]["breaking_changes"])
        if breaking_changes > 2:
            reasons.append(f"Muitas breaking changes ({breaking_changes})")
            
        return " | ".join(reasons)
    
    def _calculate_improvement_trend(self) -> float:
        """Calcula tendência de melhoria nas últimas iterações."""
        if len(self.history) < 3:
            return 1.0
            
        last_three = self.history[-3:]
        improvements = []
        
        for curr, prev in zip(last_three[1:], last_three[:-1]):
            # Considera múltiplos fatores na melhoria
            complexity_reduction = prev.get("complexity", 0) - curr.get("complexity", 0)
            changes_impact = curr["total_changes"] - prev["total_changes"]
            cohesion_improvement = curr.get("cohesion", 0) - prev.get("cohesion", 0)
            
            # Pondera os fatores
            improvement = (
                0.4 * complexity_reduction +
                0.4 * changes_impact +
                0.2 * cohesion_improvement
            )
            improvements.append(improvement)
        
        return sum(improvements) / len(improvements)
    
    def _save_history(self) -> None:
        """Salva histórico de refatorações."""
        try:
            history_data = []
            for entry in self.history:
                if isinstance(entry, dict):
                    history_data.append(entry)
                else:
                    history_data.append(entry.__dict__)
                    
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {e}")
    
    def get_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no histórico e métricas."""
        if not self.history:
            return ["Nenhuma refatoração registrada ainda"]
            
        recommendations = []
        current = self.history[-1]
        
        # Recomendações baseadas em padrões de mudança
        if current.get("removed", 0) > current.get("simplified", 0):
            recommendations.append(
                "Considere simplificar mais ao invés de remover código"
            )
            
        if current.get("consolidated", 0) > current.get("updated", 0):
            recommendations.append(
                "Foco excessivo em consolidação, considere melhorias pontuais"
            )
            
        # Recomendações baseadas em métricas de código
        for file_path, metrics in self.file_metrics.items():
            if metrics.cyclomatic_complexity > self.thresholds["max_complexity"] * 0.8:
                recommendations.append(
                    f"Complexidade alta em {file_path}, considere refatorar"
                )
                
            if metrics.module_cohesion < self.thresholds["min_cohesion"] * 1.2:
                recommendations.append(
                    f"Baixa coesão em {file_path}, considere reorganizar"
                )
                
            if metrics.coupling_score > self.thresholds["max_coupling"] * 0.8:
                recommendations.append(
                    f"Alto acoplamento em {file_path}, considere desacoplar"
                )
        
        # Recomendações baseadas em tendências
        if len(self.history) >= 3:
            trend = self._calculate_improvement_trend()
            if trend < 0.5:
                recommendations.append(
                    "Tendência de melhorias está diminuindo significativamente"
                )
                
        return recommendations or ["Nenhuma recomendação específica no momento"] 