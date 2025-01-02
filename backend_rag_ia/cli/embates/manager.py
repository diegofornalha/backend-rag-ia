"""
Gerenciador de embates.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import Embate
from .storage import SupabaseStorage

class EmbateManager:
    """Gerencia embates e suas interações."""
    
    def __init__(self, storage: Optional[SupabaseStorage] = None):
        """
        Inicializa o gerenciador.
        
        Args:
            storage: Storage opcional para persistência
        """
        self.storage = storage or SupabaseStorage()
        
    async def create_embate(self, embate: Embate) -> Dict:
        """
        Cria um novo embate.
        
        Args:
            embate: Embate para criar
            
        Returns:
            Dados do embate criado
        """
        # Valida tipo
        if embate.tipo not in ["tecnico", "preferencia", "sistema"]:
            raise ValueError("Tipo de embate inválido")
            
        # Valida status
        if embate.status not in ["aberto", "resolvido"]:
            raise ValueError("Status de embate inválido")
            
        # Salva embate
        result = await self.storage.save_embate(embate)
        return result
        
    async def update_embate(self, embate_id: str, updates: Dict) -> Dict:
        """
        Atualiza um embate existente.
        
        Args:
            embate_id: ID do embate
            updates: Dados para atualizar
            
        Returns:
            Dados atualizados
        """
        # Valida campos
        if "tipo" in updates and updates["tipo"] not in ["tecnico", "preferencia", "sistema"]:
            raise ValueError("Tipo de embate inválido")
            
        if "status" in updates and updates["status"] not in ["aberto", "resolvido"]:
            raise ValueError("Status de embate inválido")
            
        # Se resolvendo, adiciona data
        if updates.get("status") == "resolvido":
            updates["data_resolucao"] = datetime.now()
            
        # Atualiza embate
        result = await self.storage.update_embate(embate_id, updates)
        return result
        
    async def search_embates(self, query: str) -> List[Dict]:
        """
        Busca embates.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Lista de embates encontrados
        """
        return await self.storage.search_embates(query)
        
    async def export_embates(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Exporta embates.
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            Lista de embates
        """
        return await self.storage.export_embates(filters)
        
    async def get_embate(self, embate_id: str) -> Optional[Dict]:
        """
        Busca um embate específico.
        
        Args:
            embate_id: ID do embate
            
        Returns:
            Dados do embate ou None se não encontrado
        """
        embates = await self.storage.search_embates(embate_id)
        return embates[0] if embates else None 