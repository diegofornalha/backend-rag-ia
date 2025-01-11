from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

class EmbateStrategy(ABC):
    """Interface base para estratégias de embates"""
    
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um embate usando a estratégia específica"""
        pass
        
    @abstractmethod
    async def validate(self, context: Dict[str, Any]) -> bool:
        """Valida se o contexto é adequado para esta estratégia"""
        pass
        
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas específicas da estratégia"""
        pass
        
class EmbateContext:
    """Contexto que mantém a estratégia atual"""
    
    def __init__(self, strategy: Optional[EmbateStrategy] = None):
        self._strategy = strategy
        
    async def set_strategy(self, strategy: EmbateStrategy):
        """Define uma nova estratégia"""
        self._strategy = strategy
        
    async def execute_strategy(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a estratégia atual"""
        if not self._strategy:
            raise ValueError("Estratégia não definida")
            
        if not await self._strategy.validate(context):
            raise ValueError("Contexto inválido para a estratégia atual")
            
        return await self._strategy.process(context) 