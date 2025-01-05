"""
Classe base para providers de LLMs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseProvider(ABC):
    """Classe base para providers de LLMs."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        Processa uma conversa com o modelo.
        
        Args:
            messages: Lista de mensagens no formato {role: str, content: str}
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Dict com a resposta do modelo
        """
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Gera texto a partir de um prompt.
        
        Args:
            prompt: O prompt para geração
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Dict com a resposta do modelo
        """
        pass 