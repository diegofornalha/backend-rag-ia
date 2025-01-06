"""
Hooks para o sistema de embates.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .manager import EmbateManager
from .models import Embate


class EmbateHooks:
    """Hooks para o sistema de embates."""

    def __init__(self, manager: Optional[EmbateManager] = None):
        """
        Inicializa os hooks.

        Args:
            manager: Gerenciador de embates opcional
        """
        self.manager = manager or EmbateManager()

    async def pre_create(self, embate: Embate) -> None:
        """
        Hook executado antes da criação de um embate.

        Args:
            embate: Embate a ser criado

        Raises:
            ValueError: Se campos obrigatórios estiverem faltando ou se detectada alucinação
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
                f"Possível alucinação detectada:\n"
                + "\n".join(
                    [f"- {i}" for i in result["indicators"]["inconsistencias"]]
                    + [f"- {d}" for d in result["indicators"]["duplicidades"]]
                )
            )

    async def post_create(self, embate: Dict[str, Any]) -> None:
        """
        Hook executado após a criação de um embate.

        Args:
            embate: Dados do embate criado
        """
        # Notifica criação
        print(f"Embate criado: {embate['titulo']}")

    async def pre_update(self, embate_id: str, updates: Dict[str, Any]) -> None:
        """
        Hook executado antes da atualização de um embate.

        Args:
            embate_id: ID do embate
            updates: Dados para atualizar
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

    async def post_update(self, embate: Dict[str, Any]) -> None:
        """
        Hook executado após a atualização de um embate.

        Args:
            embate: Dados do embate atualizado
        """
        # Notifica atualização
        print(f"Embate atualizado: {embate['titulo']}")

        # Se resolvido, notifica resolução
        if embate.get("status") == "resolvido":
            print(f"Embate resolvido: {embate['titulo']}")

    async def pre_search(self, query: str) -> str:
        """
        Hook executado antes da busca de embates.

        Args:
            query: Query de busca

        Returns:
            Query normalizada
        """
        # Normaliza query
        return query.lower().strip()

    async def post_search(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hook executado após a busca de embates.

        Args:
            results: Resultados da busca

        Returns:
            Resultados processados
        """
        # Ordena por data
        return sorted(results, key=lambda x: x.get("data_inicio", ""), reverse=True)

    async def pre_export(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Hook executado antes da exportação de embates.

        Args:
            filters: Filtros da exportação

        Returns:
            Filtros processados
        """
        # Normaliza filtros
        if filters:
            if "tipo" in filters:
                filters["tipo"] = filters["tipo"].lower()

            if "status" in filters:
                filters["status"] = filters["status"].lower()

        return filters or {}

    async def post_export(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hook executado após a exportação de embates.

        Args:
            results: Resultados da exportação

        Returns:
            Resultados processados
        """
        # Adiciona metadados
        for result in results:
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["exportado_em"] = datetime.now().isoformat()

        return results
