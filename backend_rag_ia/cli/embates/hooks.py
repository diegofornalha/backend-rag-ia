"""Hooks para o sistema de embates.

Este módulo fornece hooks para o sistema de embates, permitindo
a execução de ações antes e depois de operações principais.
"""

from datetime import datetime
from typing import Any, Optional

from .manager import EmbateManager
from .models import Embate


class EmbateHooks:
    """Hooks para o sistema de embates.

    Esta classe fornece hooks que são executados antes e depois
    das principais operações do sistema de embates.

    Attributes
    ----------
    manager : EmbateManager
        Gerenciador de embates.

    """

    def __init__(self, manager: Optional[EmbateManager] = None):
        """Inicializa os hooks.

        Parameters
        ----------
        manager : Optional[EmbateManager], optional
            Gerenciador de embates opcional, por padrão None.

        """
        self.manager = manager or EmbateManager()

    async def pre_create(self, embate: Embate) -> None:
        """Execute validações antes da criação de um embate.

        Parameters
        ----------
        embate : Embate
            Embate a ser criado.

        Raises
        ------
        ValueError
            Se campos obrigatórios estiverem faltando ou se detectada alucinação.

        """
        # Valida campos obrigatórios
        if not embate.titulo:
            raise ValueError("Título é obrigatório")

        if not embate.contexto:
            raise ValueError("Contexto é obrigatório")

        # Normaliza tipo
        embate.tipo = embate.tipo.lower()

        # Adiciona metadados
        embate.metadata["criado_em"] = datetime.now().isoformat()

        # Detecta alucinações
        result = await self.manager.detect_hallucination(embate)
        if result["status"] == "success" and result["is_hallucination"]:
            raise ValueError(
                "Possível alucinação detectada:\n" +
                "\n".join([
                    f"- {i}" for i in result["indicators"]["inconsistencias"]
                ] + [
                    f"- {d}" for d in result["indicators"]["duplicidades"]
                ])
            )

    async def post_create(self, embate: dict[str, Any]) -> None:
        """Execute ações após a criação de um embate.

        Parameters
        ----------
        embate : dict[str, Any]
            Dados do embate criado.

        """
        # Notifica criação
        print(f"Embate criado: {embate['titulo']}")

    async def pre_update(self, embate_id: str, updates: dict[str, Any]) -> None:
        """Execute validações antes da atualização de um embate.

        Parameters
        ----------
        embate_id : str
            ID do embate.
        updates : dict[str, Any]
            Dados para atualizar.

        Raises
        ------
        ValueError
            Se campos obrigatórios estiverem vazios.

        """
        # Valida campos
        if "titulo" in updates and not updates["titulo"]:
            raise ValueError("Título não pode ser vazio")

        if "contexto" in updates and not updates["contexto"]:
            raise ValueError("Contexto não pode ser vazio")

        # Normaliza tipo
        if "tipo" in updates:
            updates["tipo"] = updates["tipo"].lower()

        # Adiciona metadados
        if "metadata" not in updates:
            updates["metadata"] = {}
        updates["metadata"]["atualizado_em"] = datetime.now().isoformat()

    async def post_update(self, embate: dict[str, Any]) -> None:
        """Execute ações após a atualização de um embate.

        Parameters
        ----------
        embate : dict[str, Any]
            Dados do embate atualizado.

        """
        # Notifica atualização
        print(f"Embate atualizado: {embate['titulo']}")

        # Se resolvido, notifica resolução
        if embate.get("status") == "resolvido":
            print(f"Embate resolvido: {embate['titulo']}")

    async def pre_search(self, query: str) -> str:
        """Execute normalização antes da busca de embates.

        Parameters
        ----------
        query : str
            Query de busca.

        Returns
        -------
        str
            Query normalizada.

        """
        # Normaliza query
        return query.lower().strip()

    async def post_search(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute processamento após a busca de embates.

        Parameters
        ----------
        results : list[dict[str, Any]]
            Resultados da busca.

        Returns
        -------
        list[dict[str, Any]]
            Resultados processados.

        """
        # Ordena por data
        return sorted(
            results,
            key=lambda x: x.get("data_inicio", ""),
            reverse=True
        )

    async def pre_export(self, filters: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Execute normalização antes da exportação de embates.

        Parameters
        ----------
        filters : Optional[dict[str, Any]], optional
            Filtros da exportação, por padrão None.

        Returns
        -------
        dict[str, Any]
            Filtros processados.

        """
        # Normaliza filtros
        if filters:
            if "tipo" in filters:
                filters["tipo"] = filters["tipo"].lower()

            if "status" in filters:
                filters["status"] = filters["status"].lower()

        return filters or {}

    async def post_export(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute processamento após a exportação de embates.

        Parameters
        ----------
        results : list[dict[str, Any]]
            Resultados da exportação.

        Returns
        -------
        list[dict[str, Any]]
            Resultados processados.

        """
        # Adiciona metadados
        for result in results:
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["exportado_em"] = datetime.now().isoformat()

        return results
