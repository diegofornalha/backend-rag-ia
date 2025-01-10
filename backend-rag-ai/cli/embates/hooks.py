"""
Hooks para o sistema de embates.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .manager import EmbateManager
from .models import Embate
from .validators.render_config import RenderConfigValidator
from .validators.render_deploy import RenderDeployValidator


class EmbateHooks:
    """Hooks para o sistema de embates."""

    def __init__(self, manager: EmbateManager | None = None):
        """
        Inicializa os hooks.

        Args:
            manager: Gerenciador de embates opcional
        """
        self.manager = manager or EmbateManager()
        self.render_validator = RenderConfigValidator()
        self.deploy_validator = RenderDeployValidator()

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
                "Possível alucinação detectada:\n"
                + "\n".join(
                    [f"- {i}" for i in result["indicators"]["inconsistencias"]]
                    + [f"- {d}" for d in result["indicators"]["duplicidades"]]
                )
            )

        # Valida render.yaml se o embate for relacionado a deploy
        if "deploy" in embate.tipo or "deploy" in embate.contexto.lower():
            # Validação de configuração
            if self.render_validator.has_config_changed():
                errors = self.render_validator.validate()
                if errors:
                    raise ValueError(
                        "Configuração do render.yaml inválida:\n"
                        + "\n".join(f"- {e}" for e in errors)
                    )
                self.render_validator.save_validation_state()

            # Validação de deploy
            deploy_errors = self.deploy_validator.validate()
            if deploy_errors:
                raise ValueError(
                    "Problemas detectados que podem causar falha no deploy:\n"
                    + "\n".join(f"- {e}" for e in deploy_errors)
                )
            self.deploy_validator.save_validation_state()

    async def post_create(self, embate: dict[str, Any]) -> None:
        """
        Hook executado após a criação de um embate.

        Args:
            embate: Dados do embate criado
        """
        # Notifica criação
        print(f"Embate criado: {embate['titulo']}")

    async def pre_update(self, embate_id: str, updates: dict[str, Any]) -> None:
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

        # Valida render.yaml se a atualização for relacionada a deploy
        if (
            "tipo" in updates
            and "deploy" in updates["tipo"]
            or "contexto" in updates
            and "deploy" in updates["contexto"].lower()
        ):
            # Validação de configuração
            if self.render_validator.has_config_changed():
                errors = self.render_validator.validate()
                if errors:
                    raise ValueError(
                        "Configuração do render.yaml inválida:\n"
                        + "\n".join(f"- {e}" for e in errors)
                    )
                self.render_validator.save_validation_state()

            # Validação de deploy
            deploy_errors = self.deploy_validator.validate()
            if deploy_errors:
                raise ValueError(
                    "Problemas detectados que podem causar falha no deploy:\n"
                    + "\n".join(f"- {e}" for e in deploy_errors)
                )
            self.deploy_validator.save_validation_state()

    async def post_update(self, embate: dict[str, Any]) -> None:
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

            # Se for um embate de deploy, salva o estado de validação
            if "deploy" in embate.get("tipo", "").lower() or "deploy" in embate.get("contexto", "").lower():
                self.deploy_validator.save_validation_state()

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

    async def post_search(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Hook executado após a busca de embates.

        Args:
            results: Resultados da busca

        Returns:
            Resultados processados
        """
        # Ordena por data
        return sorted(results, key=lambda x: x.get("data_inicio", ""), reverse=True)

    async def pre_export(self, filters: dict[str, Any] | None = None) -> dict[str, Any]:
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

    async def post_export(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

            # Se for um embate de deploy, adiciona estado de validação
            if "deploy" in result.get("tipo", "").lower() or "deploy" in result.get("contexto", "").lower():
                deploy_state = self.deploy_validator.load_validation_state()
                result["metadata"]["deploy_validation"] = deploy_state

        return results
