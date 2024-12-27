from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings

class BaseCluster(ABC):
    """Classe base para todos os clusters"""
    
    def __init__(self, settings: BaseSettings):
        self.settings = settings
        
    @abstractmethod
    async def get_documents_count(self) -> int:
        """Retorna a contagem de documentos"""
        pass
        
    @abstractmethod
    async def get_embeddings_count(self) -> int:
        """Retorna a contagem de embeddings"""
        pass
        
    @abstractmethod
    async def get_health_check(self) -> Dict[str, Any]:
        """Retorna informações de saúde do cluster"""
        pass
        
    @abstractmethod
    async def update_documents_count(self) -> Optional[int]:
        """Atualiza a contagem de documentos"""
        pass 