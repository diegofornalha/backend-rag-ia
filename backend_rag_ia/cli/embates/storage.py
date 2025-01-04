"""Storage para embates.

Este módulo fornece implementações de storage para embates,
incluindo uma implementação em memória para testes.
"""

from datetime import datetime
from typing import Optional

from .models import Embate


class MemoryStorage:
    """Storage em memória para testes.

    Esta classe fornece uma implementação simples de storage em memória,
    útil para testes e desenvolvimento.

    Attributes
    ----------
    embates : dict[str, Embate]
        Dicionário de embates armazenados em memória.

    """

    def __init__(self):
        """Inicializa o storage em memória."""
        self.embates: dict[str, Embate] = {}

    async def save(self, embate: Embate) -> dict:
        """Salva um embate no storage.

        Parameters
        ----------
        embate : Embate
            Embate a ser salvo.

        Returns
        -------
        dict
            Dicionário contendo o ID do embate salvo.

        """
        if not embate.id:
            embate.id = f"local-{datetime.now().isoformat()}"

        self.embates[embate.id] = embate
        return {"data": {"id": embate.id}}

    async def get(self, id: str) -> Optional[Embate]:
        """Busca um embate por ID.

        Parameters
        ----------
        id : str
            ID do embate a ser buscado.

        Returns
        -------
        Optional[Embate]
            Embate encontrado ou None se não encontrado.

        """
        return self.embates.get(id)

    async def list(self) -> list[Embate]:
        """Lista todos os embates.

        Returns
        -------
        list[Embate]
            Lista de todos os embates armazenados.

        """
        return list(self.embates.values())

    async def delete(self, id: str) -> None:
        """Remove um embate do storage.

        Parameters
        ----------
        id : str
            ID do embate a ser removido.

        """
        if id in self.embates:
            del self.embates[id]
