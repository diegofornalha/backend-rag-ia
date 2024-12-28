from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from config.config import Settings

class BaseCluster(ABC):
    """Classe base para todos os clusters"""
    
    def __init__(self, settings: Settings):
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

    @abstractmethod
    async def create_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Cria embeddings para um documento
        
        Args:
            document_id: ID do documento
            text: Texto para gerar embeddings
            
        Returns:
            Dicionário com informações dos embeddings gerados
        """
        pass

    @abstractmethod
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Busca documentos similares baseado em uma query
        
        Args:
            query: Texto da busca
            limit: Número máximo de resultados
            
        Returns:
            Lista de documentos similares
        """
        pass

    @abstractmethod
    async def delete_embeddings(self, document_id: str) -> bool:
        """Remove embeddings de um documento
        
        Args:
            document_id: ID do documento
            
        Returns:
            True se removido com sucesso
        """
        pass

    @abstractmethod
    async def update_embeddings(self, document_id: str, text: str) -> Dict[str, Any]:
        """Atualiza embeddings de um documento
        
        Args:
            document_id: ID do documento
            text: Novo texto para gerar embeddings
            
        Returns:
            Dicionário com informações dos embeddings atualizados
        """
        pass 