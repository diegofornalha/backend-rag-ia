"""
Módulo para verificação e controle de complexidade do sistema.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ComplexityMetrics:
    """Métricas de complexidade do sistema."""
    dependencies_count: int
    integration_points: int
    maintenance_score: float
    stability_score: float
    understanding_score: float

class ComplexityChecker:
    """Classe para verificar e controlar a complexidade do sistema."""
    
    def __init__(self):
        """Inicializa o verificador de complexidade."""
        self.thresholds = {
            "max_dependencies": 20,  # Número máximo de dependências
            "max_integration_points": 10,  # Número máximo de pontos de integração
            "min_maintenance_score": 0.7,  # Score mínimo de manutenibilidade (0-1)
            "min_stability_score": 0.8,  # Score mínimo de estabilidade (0-1)
            "min_understanding_score": 0.7,  # Score mínimo de compreensão (0-1)
        }
        
        self.warnings: List[Dict] = []
        self.last_check: Optional[datetime] = None
    
    async def check_complexity(self) -> ComplexityMetrics:
        """Verifica a complexidade atual do sistema."""
        try:
            # Coleta métricas
            metrics = ComplexityMetrics(
                dependencies_count=await self._count_dependencies(),
                integration_points=await self._count_integration_points(),
                maintenance_score=await self._calculate_maintenance_score(),
                stability_score=await self._calculate_stability_score(),
                understanding_score=await self._calculate_understanding_score()
            )
            
            # Registra verificação
            self.last_check = datetime.now()
            
            # Verifica limites
            await self._check_thresholds(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao verificar complexidade: {e}")
            raise
    
    async def _count_dependencies(self) -> int:
        """Conta número de dependências do sistema."""
        # TODO: Implementar contagem real de dependências
        return 15  # Placeholder
    
    async def _count_integration_points(self) -> int:
        """Conta pontos de integração do sistema."""
        # TODO: Implementar contagem real de integrações
        return 8  # Placeholder
    
    async def _calculate_maintenance_score(self) -> float:
        """Calcula score de manutenibilidade."""
        # TODO: Implementar cálculo real
        return 0.75  # Placeholder
    
    async def _calculate_stability_score(self) -> float:
        """Calcula score de estabilidade."""
        # TODO: Implementar cálculo real
        return 0.85  # Placeholder
    
    async def _calculate_understanding_score(self) -> float:
        """Calcula score de compreensão do código."""
        # TODO: Implementar cálculo real
        return 0.80  # Placeholder
    
    async def _check_thresholds(self, metrics: ComplexityMetrics) -> None:
        """Verifica se as métricas estão dentro dos limites."""
        if metrics.dependencies_count > self.thresholds["max_dependencies"]:
            self.warnings.append({
                "type": "dependencies",
                "message": f"Número de dependências ({metrics.dependencies_count}) excede o limite ({self.thresholds['max_dependencies']})",
                "timestamp": datetime.now()
            })
        
        if metrics.integration_points > self.thresholds["max_integration_points"]:
            self.warnings.append({
                "type": "integrations",
                "message": f"Número de integrações ({metrics.integration_points}) excede o limite ({self.thresholds['max_integration_points']})",
                "timestamp": datetime.now()
            })
        
        if metrics.maintenance_score < self.thresholds["min_maintenance_score"]:
            self.warnings.append({
                "type": "maintenance",
                "message": f"Score de manutenção ({metrics.maintenance_score:.2f}) abaixo do mínimo ({self.thresholds['min_maintenance_score']})",
                "timestamp": datetime.now()
            })
        
        if metrics.stability_score < self.thresholds["min_stability_score"]:
            self.warnings.append({
                "type": "stability",
                "message": f"Score de estabilidade ({metrics.stability_score:.2f}) abaixo do mínimo ({self.thresholds['min_stability_score']})",
                "timestamp": datetime.now()
            })
        
        if metrics.understanding_score < self.thresholds["min_understanding_score"]:
            self.warnings.append({
                "type": "understanding",
                "message": f"Score de compreensão ({metrics.understanding_score:.2f}) abaixo do mínimo ({self.thresholds['min_understanding_score']})",
                "timestamp": datetime.now()
            })
    
    async def get_recommendations(self) -> List[str]:
        """Gera recomendações baseadas nos warnings atuais."""
        recommendations = []
        
        for warning in self.warnings:
            if warning["type"] == "dependencies":
                recommendations.append(
                    "Reduza o número de dependências:\n"
                    "- Consolide funcionalidades similares\n"
                    "- Remova dependências não utilizadas\n"
                    "- Considere alternativas mais leves"
                )
            
            elif warning["type"] == "integrations":
                recommendations.append(
                    "Simplifique pontos de integração:\n"
                    "- Unifique integrações similares\n"
                    "- Remova integrações desnecessárias\n"
                    "- Use padrões de integração consistentes"
                )
            
            elif warning["type"] == "maintenance":
                recommendations.append(
                    "Melhore a manutenibilidade:\n"
                    "- Refatore código complexo\n"
                    "- Melhore documentação\n"
                    "- Adicione testes automatizados"
                )
            
            elif warning["type"] == "stability":
                recommendations.append(
                    "Aumente a estabilidade:\n"
                    "- Adicione tratamento de erros\n"
                    "- Implemente circuit breakers\n"
                    "- Melhore logging e monitoramento"
                )
            
            elif warning["type"] == "understanding":
                recommendations.append(
                    "Melhore a compreensão do código:\n"
                    "- Adicione documentação clara\n"
                    "- Simplifique lógica complexa\n"
                    "- Use nomes descritivos"
                )
        
        return recommendations
    
    async def should_stop_development(self) -> bool:
        """Determina se o desenvolvimento deve ser interrompido devido à complexidade."""
        if not self.last_check or not self.warnings:
            return False
        
        # Critérios para interromper desenvolvimento:
        # 1. Mais de 3 warnings ativos
        # 2. Qualquer score abaixo de 60% do mínimo
        # 3. Dependências ou integrações 50% acima do limite
        
        if len(self.warnings) > 3:
            logger.warning("Desenvolvimento deve ser interrompido: muitos warnings ativos")
            return True
        
        metrics = await self.check_complexity()
        
        if (metrics.maintenance_score < self.thresholds["min_maintenance_score"] * 0.6 or
            metrics.stability_score < self.thresholds["min_stability_score"] * 0.6 or
            metrics.understanding_score < self.thresholds["min_understanding_score"] * 0.6):
            logger.warning("Desenvolvimento deve ser interrompido: scores muito baixos")
            return True
        
        if (metrics.dependencies_count > self.thresholds["max_dependencies"] * 1.5 or
            metrics.integration_points > self.thresholds["max_integration_points"] * 1.5):
            logger.warning("Desenvolvimento deve ser interrompido: limites muito excedidos")
            return True
        
        return False 