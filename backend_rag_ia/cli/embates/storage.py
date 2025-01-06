"""Storage para embates."""

from typing import Dict, List, Optional
from datetime import datetime

from .models import Embate


class MemoryStorage:
    """Storage em memória para testes."""

    def __init__(self):
        self.embates: Dict[str, Embate] = {}

    async def save(self, embate: Embate) -> Dict:
        """Salva um embate."""
        if not embate.id:
            embate.id = f"local-{datetime.now().isoformat()}"

        self.embates[embate.id] = embate
        return {"data": {"id": embate.id}}

    async def get(self, id: str) -> Optional[Embate]:
        """Busca um embate por ID."""
        return self.embates.get(id)

    async def list(self) -> List[Embate]:
        """Lista todos os embates."""
        return list(self.embates.values())

    async def delete(self, id: str) -> None:
        """Remove um embate."""
        if id in self.embates:
            del self.embates[id]
