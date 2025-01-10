from typing import Dict, Type
from enum import Enum

from .base_strategy import EmbateStrategy
from .multiagent_strategy import MultiagentStrategy
from .single_agent_strategy import SingleAgentStrategy
from .comparative_strategy import ComparativeStrategy

class EmbateStrategyType(Enum):
    """Tipos de estratégias disponíveis"""
    MULTIAGENT = "multiagent"
    SINGLE_AGENT = "single_agent"
    COMPARATIVE = "comparative"

class StrategyFactory:
    """Factory para criar estratégias de embates"""
    
    _strategies: Dict[EmbateStrategyType, Type[EmbateStrategy]] = {
        EmbateStrategyType.MULTIAGENT: MultiagentStrategy,
        EmbateStrategyType.SINGLE_AGENT: SingleAgentStrategy,
        EmbateStrategyType.COMPARATIVE: ComparativeStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: str) -> EmbateStrategy:
        """Cria uma nova instância da estratégia solicitada"""
        try:
            strategy_enum = EmbateStrategyType(strategy_type)
            strategy_class = cls._strategies.get(strategy_enum)
            
            if not strategy_class:
                raise ValueError(f"Estratégia não implementada: {strategy_type}")
                
            return strategy_class()
            
        except ValueError as e:
            raise ValueError(f"Tipo de estratégia inválido: {strategy_type}") from e
            
    @classmethod
    def register_strategy(
        cls,
        strategy_type: EmbateStrategyType,
        strategy_class: Type[EmbateStrategy]
    ) -> None:
        """Registra uma nova estratégia na factory"""
        cls._strategies[strategy_type] = strategy_class
        
    @classmethod
    def get_available_strategies(cls) -> list[str]:
        """Retorna lista de estratégias disponíveis"""
        return [strategy.value for strategy in EmbateStrategyType] 