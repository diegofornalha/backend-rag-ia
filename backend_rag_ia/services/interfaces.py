"""
Interfaces base para os serviços do sistema.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class SuggestionInterface(ABC):
    """Interface base para serviços de sugestão."""

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa o contexto e gera sugestões.

        Args:
            context: Contexto com dados para processamento

        Returns:
            Dicionário com sugestões geradas
        """
        pass

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Gera uma sugestão baseada no prompt.

        Args:
            prompt: Texto do prompt
            **kwargs: Argumentos adicionais

        Returns:
            Texto da sugestão gerada
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Retorna lista de capacidades do serviço.

        Returns:
            Lista de strings com capacidades
        """
        pass
