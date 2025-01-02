"""
Armazenamento de embates no Supabase.
"""

from datetime import datetime
from typing import Dict, List, Optional

from supabase import Client, create_client

from ..models import Embate

class SupabaseStorage:
    """Gerencia armazenamento de embates no Supabase."""
    
    def __init__(self, url: str, key: str):
        """
        Inicializa o storage.
        
        Args:
            url: URL do projeto Supabase
            key: Chave de API do Supabase
        """
        self.client = create_client(url, key)
        
    async def save(self, embate: Embate) -> Dict:
        """
        Salva um embate.
        
        Args:
            embate: Embate a ser salvo
            
        Returns:
            Dados do embate salvo
        """
        data = embate.dict()
        data["criado_em"] = data["criado_em"].isoformat()
        data["atualizado_em"] = data["atualizado_em"].isoformat()
        
        response = await self.client.table("embates").insert(data).execute()
        return response.data[0]
        
    async def get(self, id: str) -> Optional[Embate]:
        """
        Busca um embate por ID.
        
        Args:
            id: ID do embate
            
        Returns:
            Embate encontrado ou None
        """
        response = await self.client.table("embates").select("*").eq("id", id).execute()
        
        if not response.data:
            return None
            
        data = response.data[0]
        data["criado_em"] = datetime.fromisoformat(data["criado_em"])
        data["atualizado_em"] = datetime.fromisoformat(data["atualizado_em"])
        
        return Embate(**data)
        
    async def list(self) -> List[Embate]:
        """
        Lista todos os embates.
        
        Returns:
            Lista de embates
        """
        response = await self.client.table("embates").select("*").execute()
        
        embates = []
        for data in response.data:
            data["criado_em"] = datetime.fromisoformat(data["criado_em"])
            data["atualizado_em"] = datetime.fromisoformat(data["atualizado_em"])
            embates.append(Embate(**data))
            
        return embates
