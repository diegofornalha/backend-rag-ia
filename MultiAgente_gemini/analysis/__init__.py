"""
Análise e sugestões de melhorias.

Este cluster contém os componentes de análise:
- Análise de código
- Padrões e boas práticas
- Otimizações
- Sugestões de melhoria
"""

from .suggestions.interfaces import (
    IAgent,
    AnalysisContext,
    AnalysisResult,
    AgentRole
)

__all__ = [
    'IAgent',
    'AnalysisContext',
    'AnalysisResult',
    'AgentRole'
] 