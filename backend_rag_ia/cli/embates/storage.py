"""
Módulo para armazenamento de embates no Supabase.
"""

from backend_rag_ia.cli.embates.models import Embate
from backend_rag_ia.config.supabase_config import create_client


class SupabaseStorage:
    """Classe para armazenamento de embates no Supabase."""

    def __init__(self) -> None:
        """Inicializa o storage com um cliente Supabase."""
        self.client = create_client()

    async def save_embate(self, embate: Embate) -> dict[str, str | dict]:
        """Salva um embate no Supabase."""
        return await self.client.save_embate_with_embedding(embate)

    async def update_embate(self, embate_id: str, updates: dict) -> dict[str, str | dict]:
        """Atualiza um embate no Supabase."""
        return await self.client.update_embate(embate_id, updates)

    async def search_embates(self, query: str, limit: int | None = None) -> list[dict]:
        """Busca embates no Supabase."""
        return await self.client.search_embates(query, limit)

    async def export_embates(self, filters: dict) -> list[dict]:
        """Exporta embates do Supabase."""
        return await self.client.export_embates(filters) 