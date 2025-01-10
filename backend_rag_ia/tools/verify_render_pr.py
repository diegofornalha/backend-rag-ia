import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests
import yaml

from ..config.settings import Settings, get_settings


@dataclass
class RenderValidationResult:
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]


class RenderPRValidator:
    """Validador para Pull Requests e ambiente Render."""

    def __init__(self):
        self.settings = get_settings()
        self.root_dir = Path(__file__).parent.parent.parent
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.suggestions: list[str] = []

    def validate_render_yaml(self) -> bool:
        """Valida o arquivo render.yaml"""
        render_yaml_path = self.root_dir / "render.yaml"

        if not render_yaml_path.exists():
            self.errors.append("❌ render.yaml não encontrado")
            return False

        try:
            with open(render_yaml_path) as f:
                render_config = yaml.safe_load(f)

            # Validações essenciais
            if "services" not in render_config:
                self.errors.append("❌ Nenhum serviço definido no render.yaml")
                return False

            # Validação de previews
            previews = render_config.get("previews", {})
            if not previews.get("enable"):
                self.warnings.append("⚠️ Previews não estão habilitados no render.yaml")

            # Validação de variáveis de ambiente
            service = render_config["services"][0]
            env_vars = {ev["key"]: ev.get("sync", True) for ev in service.get("envVars", [])}

            required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
            for var in required_vars:
                if var not in env_vars:
                    self.errors.append(f"❌ Variável {var} não definida no render.yaml")
                elif env_vars[var]:
                    self.warnings.append(f"⚠️ Variável sensível {var} está com sync=true")

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"❌ Erro ao ler render.yaml: {str(e)}")
            return False

    def validate_settings(self) -> bool:
        """Valida as configurações do settings.py"""
        try:
            # Verifica se o settings está configurado corretamente para previews
            if not hasattr(self.settings, "is_preview_environment"):
                self.errors.append("❌ Método is_preview_environment não encontrado em settings")
                return False

            # Verifica CORS para previews
            if not self.settings.cors_origins_list:
                self.warnings.append("⚠️ Nenhuma origem CORS configurada para previews")

            # Verifica URLs
            if not self.settings.active_url:
                self.errors.append("❌ URL ativa não configurada")
                return False

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"❌ Erro ao validar settings: {str(e)}")
            return False

    def validate_docker_setup(self) -> bool:
        """Valida a configuração do Docker"""
        dockerfile_path = self.root_dir / "Dockerfile"

        if not dockerfile_path.exists():
            self.errors.append("❌ Dockerfile não encontrado")
            return False

        try:
            with open(dockerfile_path) as f:
                dockerfile = f.read()

            # Verifica configurações essenciais
            checks = {
                "PYTHONPATH": "ENV PYTHONPATH" in dockerfile,
                "PORT": "ENV PORT" in dockerfile,
                "WORKDIR": "WORKDIR /app" in dockerfile,
            }

            for key, exists in checks.items():
                if not exists:
                    self.errors.append(f"❌ Configuração {key} não encontrada no Dockerfile")

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"❌ Erro ao validar Dockerfile: {str(e)}")
            return False

    def validate_health_check(self) -> bool:
        """Valida o endpoint de health check"""
        try:
            health_url = f"{self.settings.active_url}/api/v1/health"
            response = requests.get(health_url)

            if response.status_code != 200:
                self.errors.append(f"❌ Health check falhou: {response.status_code}")
                return False

            return True

        except Exception as e:
            self.warnings.append(f"⚠️ Não foi possível validar health check: {str(e)}")
            return False

    def run_validation(self) -> RenderValidationResult:
        """Executa todas as validações"""
        validations = [
            self.validate_render_yaml(),
            self.validate_settings(),
            self.validate_docker_setup(),
            self.validate_health_check(),
        ]

        is_valid = all(validations)

        # Adiciona sugestões de melhoria
        if is_valid and not self.errors:
            self.suggestions.extend(
                [
                    "💡 Considere adicionar testes automatizados para o ambiente de preview",
                    "💡 Documente o processo de preview no README",
                    "💡 Configure notificações para falhas no preview",
                ]
            )

        return RenderValidationResult(
            is_valid=is_valid,
            errors=self.errors,
            warnings=self.warnings,
            suggestions=self.suggestions,
        )


def main():
    """Função principal para execução via CLI"""
    validator = RenderPRValidator()
    result = validator.run_validation()

    # Exibe resultados
    if result.errors:
        print("\n🔴 Erros encontrados:")
        for error in result.errors:
            print(error)

    if result.warnings:
        print("\n🟡 Avisos:")
        for warning in result.warnings:
            print(warning)

    if result.suggestions:
        print("\n💭 Sugestões:")
        for suggestion in result.suggestions:
            print(suggestion)

    # Status final
    if result.is_valid:
        print("\n✅ Validação concluída com sucesso!")
        sys.exit(0)
    else:
        print("\n❌ Falha na validação")
        sys.exit(1)


if __name__ == "__main__":
    main()
