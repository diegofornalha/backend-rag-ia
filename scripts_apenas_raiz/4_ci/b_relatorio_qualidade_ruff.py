"""CLI para gerar relatório de qualidade de código usando Ruff."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

# Ajusta path para acessar utils
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend_rag_ia.utils.logging_config import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Console para output
console = Console()


def execute_ruff(directory: Path) -> list[dict[str, Any]]:
    """Executa Ruff e retorna violações.

    Args:
        directory: Diretório para analisar

    Returns:
        Lista de violações encontradas
    """
    try:
        # Executa Ruff com output JSON
        result = subprocess.run(
            [
                "ruff",
                "check",
                str(directory),
                "--format=json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Carrega resultado
        if result.stdout:
            return json.loads(result.stdout)
        return []

    except subprocess.CalledProcessError as e:
        logger.exception("Erro ao executar Ruff: %s", e)
        return []

    except json.JSONDecodeError as e:
        logger.exception("Erro ao decodificar resultado: %s", e)
        return []


def group_violations(violations: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Agrupa violações por regra.

    Args:
        violations: Lista de violações

    Returns:
        Dicionário com violações agrupadas por regra
    """
    grouped: dict[str, list[dict[str, Any]]] = {}

    for violation in violations:
        rule = violation.get("code", "unknown")
        if rule not in grouped:
            grouped[rule] = []
        grouped[rule].append(violation)

    return grouped


def generate_statistics(violations: list[dict[str, Any]]) -> dict[str, Any]:
    """Gera estatísticas das violações.

    Args:
        violations: Lista de violações

    Returns:
        Dicionário com estatísticas
    """
    # Agrupa por regra
    grouped = group_violations(violations)

    # Conta violações por regra
    rule_counts = {
        rule: len(violations)
        for rule, violations in grouped.items()
    }

    # Calcula totais
    total_violations = len(violations)
    total_files = len({v.get("path") for v in violations})

    return {
        "total_violations": total_violations,
        "total_files": total_files,
        "violations_by_rule": rule_counts,
        "date": date.today().isoformat(),
    }


def display_report(stats: dict[str, Any]) -> None:
    """Exibe relatório formatado.

    Args:
        stats: Estatísticas das violações
    """
    # Cabeçalho
    console.print(f"\n📊 Relatório de Qualidade de Código - {stats['date']}")
    console.print(f"\nTotal de violações: {stats['total_violations']}")
    console.print(f"Arquivos afetados: {stats['total_files']}")

    # Tabela de violações por regra
    if stats["violations_by_rule"]:
        table = Table(title="\nViolações por Regra")
        table.add_column("Regra", style="cyan")
        table.add_column("Quantidade", justify="right", style="green")

        for rule, count in sorted(
            stats["violations_by_rule"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            table.add_row(rule, str(count))

        console.print(table)
    else:
        console.print("\n✨ Nenhuma violação encontrada!")


def main() -> None:
    """Função principal."""
    try:
        # Verifica argumentos
        if len(sys.argv) < 2:
            console.print("\n❌ Uso: python b_relatorio_qualidade_ruff.py <directory>")
            console.print("\nExemplo: python b_relatorio_qualidade_ruff.py backend_rag_ia/")
            sys.exit(1)

        # Obtém diretório
        directory = Path(sys.argv[1])

        if not directory.exists():
            console.print(f"\n❌ Diretório não encontrado: {directory}")
            sys.exit(1)

        # Executa análise
        console.print(f"\n🔍 Analisando código em: {directory}")
        violations = execute_ruff(directory)

        # Gera relatório
        stats = generate_statistics(violations)
        display_report(stats)

    except KeyboardInterrupt:
        console.print("\n\n👋 Análise interrompida!")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
