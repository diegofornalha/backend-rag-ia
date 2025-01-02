"""
Armazenamento de embates.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .models import Embate

class SupabaseStorage:
    """Armazenamento de embates usando Supabase."""
    
    def __init__(self, client=None):
        """
        Inicializa o storage.
        
        Args:
            client: Cliente Supabase opcional
        """
        self.client = client
        
    async def save_embate(self, embate: Embate) -> Dict:
        """
        Salva um embate.
        
        Args:
            embate: Embate para salvar
            
        Returns:
            Dados do embate salvo
        """
        if not self.client:
            # Fallback para arquivo local
            return self._save_local(embate)
            
        data = embate.model_dump()
        response = await self.client.table("rag.embates").insert(data).execute()
        
        return {
            "id": response.data[0]["id"],
            "status": "success",
            "data": response.data[0]
        }
        
    async def update_embate(self, embate_id: str, updates: Dict) -> Dict:
        """
        Atualiza um embate.
        
        Args:
            embate_id: ID do embate
            updates: Dados para atualizar
            
        Returns:
            Dados atualizados
        """
        if not self.client:
            return {"status": "error", "message": "Cliente não configurado"}
            
        response = await self.client.table("rag.embates").update(updates).eq("id", embate_id).execute()
        
        return {
            "id": embate_id,
            "status": "success",
            "data": response.data[0]
        }
        
    async def search_embates(self, query: str) -> List[Dict]:
        """
        Busca embates.
        
        Args:
            query: Texto para buscar
            
        Returns:
            Lista de embates encontrados
        """
        if not self.client:
            return []
            
        response = await self.client.table("rag.embates").select("*").textSearch("titulo", query).execute()
        
        return response.data
        
    async def export_embates(self, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Exporta embates.
        
        Args:
            filters: Filtros opcionais
            
        Returns:
            Lista de embates
        """
        if not self.client:
            return []
            
        query = self.client.table("rag.embates").select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
                
        response = await query.execute()
        
        return response.data
        
    def _save_local(self, embate: Embate) -> Dict:
        """Salva embate localmente quando não há cliente."""
        if not embate.arquivo:
            embate.arquivo = f"embate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
        path = Path(embate.arquivo)
        path.write_text(embate.model_dump_json(indent=2))
        
        return {
            "status": "success",
            "data": embate.model_dump()
        } 