"""
Interfaces para o sistema de continuidade.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional

class AgentRole(Enum):
    """Papéis possíveis dos agentes."""
    CURSOR_AI = "cursor_ai"
    RESEARCHER = "researcher"
    CRITIC = "critic"
    IMPROVER = "improver"
    SYNTHESIZER = "synthesizer"

@dataclass
class AnalysisContext:
    """Contexto para análise."""
    project_path: str
    files: List[str]
    config: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class AnalysisResult:
    """Resultado da análise."""
    agent_name: str
    findings: Dict[str, Any]
    recommendations: List[str]
    priority: int
    metadata: Dict[str, Any]

class IAgent(ABC):
    """Interface base para agentes."""
    
    @abstractmethod
    def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Analisa o contexto e retorna resultados."""
        pass
    
    @abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processa uma mensagem e retorna resposta."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Retorna lista de capacidades do agente."""
        pass 