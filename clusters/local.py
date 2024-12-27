from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseCluster

class LocalCluster(BaseCluster):
    """Implementação do cluster para ambiente local"""
    
    async def get_documents_count(self) -> int:
        """Retorna a contagem fixa de documentos para ambiente local"""
        return self.settings.DOCUMENTS_COUNT
        
    async def get_embeddings_count(self) -> int:
        """Retorna a contagem fixa de embeddings para ambiente local"""
        return self.settings.EMBEDDINGS_COUNT
        
    async def get_health_check(self) -> Dict[str, Any]:
        """Retorna informações de saúde do cluster local"""
        return {
            "status": "healthy",
            "message": "API está funcionando normalmente",
            "documents_count": await self.get_documents_count(),
            "embeddings_count": await self.get_embeddings_count(),
            "environment": self.settings.ENVIRONMENT,
            "timestamp": datetime.now().isoformat()
        }
        
    async def update_documents_count(self) -> Optional[int]:
        """No ambiente local, apenas retorna a contagem fixa"""
        return self.settings.DOCUMENTS_COUNT 