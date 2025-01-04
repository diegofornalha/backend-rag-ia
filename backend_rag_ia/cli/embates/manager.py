"""Módulo para gerenciamento de embates.

Este módulo contém classes e funções para gerenciar embates,
incluindo análise de impacto, execução de mudanças e resolução de conflitos.
"""

from datetime import datetime
from typing import Any, Optional

from .models import Embate
from .storage import SupabaseStorage


class ConflictResolver:
    """Resolve conflitos entre embates."""

    def __init__(self) -> None:
        self.conflitos: list[dict] = []

    def detectar_conflito(self, embate1: Embate, embate2: Embate) -> bool:
        """Detecta conflito entre dois embates."""
        if embate1.tipo == embate2.tipo:
            return self._contexto_similar(embate1.contexto, embate2.contexto)
        return False

    def _contexto_similar(self, ctx1: str, ctx2: str) -> bool:
        """Verifica se dois contextos são similares."""
        palavras1 = set(ctx1.lower().split())
        palavras2 = set(ctx2.lower().split())
        intersecao = palavras1.intersection(palavras2)
        return len(intersecao) / max(len(palavras1), len(palavras2)) > 0.7


class EmbateManager:
    """Gerencia embates."""

    def __init__(self, storage: Optional[SupabaseStorage] = None) -> None:
        self.storage = storage
        self.resolver = ConflictResolver()

    async def create_embate(self, embate: Embate) -> dict[str, Any]:
        """Cria um novo embate."""
        try:
            if self.storage:
                embates = await self.storage.list()
                for e in embates:
                    if self.resolver.detectar_conflito(embate, e):
                        self.resolver.registrar_conflito(embate, e)
                        embate = self.resolver.resolver_conflito(embate, e)

                result = await self.storage.save(embate)
                return {"status": "success", "id": result["data"]["id"]}

            return {
                "status": "success",
                "id": "local-" + datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_embate(self, id: str) -> Optional[Embate]:
        """Busca um embate por ID."""
        if self.storage:
            return await self.storage.get(id)
        return None

    async def list_embates(self) -> list[Embate]:
        """Lista todos os embates."""
        if self.storage:
            return await self.storage.list()
        return []
