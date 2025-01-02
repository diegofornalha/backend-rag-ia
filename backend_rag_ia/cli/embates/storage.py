"""
Armazenamento de embates no Supabase.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from .models import Embate

class SupabaseStorage:
    """Classe para armazenamento de embates no Supabase."""
    
    def __init__(self):
        """Inicializa o cliente Supabase."""
        self.client = create_client(
            supabase_url="https://your-project.supabase.co",
            supabase_key="your-anon-key"
        )
        
    async def save_embate(self, embate: Embate) -> Dict[str, Any]:
        """Salva um embate no Supabase."""
        data = embate.model_dump()
        data["data_inicio"] = data["data_inicio"].isoformat()
        if data.get("data_resolucao"):
            data["data_resolucao"] = data["data_resolucao"].isoformat()
            
        result = await self.client.table("embates").insert(data).execute()
        return result
        
    async def update_embate(self, embate_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Atualiza um embate no Supabase."""
        if "data_resolucao" in updates and isinstance(updates["data_resolucao"], datetime):
            updates["data_resolucao"] = updates["data_resolucao"].isoformat()
            
        result = await self.client.table("embates").update(updates).eq("id", embate_id).execute()
        return result
        
    async def search_embates(self, query: str) -> List[Dict[str, Any]]:
        """Busca embates no Supabase."""
        result = await self.client.table("embates").select("*").textSearch("titulo", query).execute()
        return result.data
        
    async def export_embates(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Exporta embates do Supabase."""
        query = self.client.table("embates").select("*")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
                
        result = await query.execute()
        return result.data 