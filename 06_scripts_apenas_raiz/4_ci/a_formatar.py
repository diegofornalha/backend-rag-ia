#!/usr/bin/env python3
"""Script para formatar código Python usando Ruff."""

from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


def run_ruff(directory: str, fix: bool = True) -> tuple[bool, list[str]]:
    """Executa o Ruff em um diretório.

    Args:
        directory: Caminho do diretório para formatar
        fix: Se True, aplica correções automáticas

    Returns:
        Tupla com (passou, lista_de_erros)
    """
    try:
        cmd = ["ruff", "check", directory]
        if fix:
            cmd.append("--fix")

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            console.print(f"[green]✅ {directory} passou na verificação do Ruff![/green]")
            return True, []

        errors = result.stdout.strip().split("\n")
        console.print(f"[yellow]⚠️ Ruff encontrou {len(errors)} problemas[/yellow]")
        return False, errors

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Erro ao executar Ruff: {e!s}[/red]")
        return False, [str(e)]


def run_mypy(directory: str) -> tuple[bool, list[str]]:
    """Executa o MyPy para verificação de tipos.

    Args:
        directory: Caminho do diretório para verificar

    Returns:
        Tupla com (passou, lista_de_erros)
    """
    try:
        result = subprocess.run(
            [
                "mypy",
                "--ignore-missing-imports",
                "--check-untyped-defs",
                directory,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            console.print(f"[green]✅ {directory} passou na verificação do MyPy![/green]")
            return True, []

        errors = result.stdout.strip().split("\n")
        console.print(f"[yellow]⚠️ MyPy encontrou {len(errors)} problemas[/yellow]")
        return False, errors

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Erro ao executar MyPy: {e!s}[/red]")
        return False, [str(e)]


def format_directory(directory: str, check_types: bool = True, max_attempts: int = 3) -> bool:
    """Formata e verifica um diretório usando Ruff e MyPy.

    Args:
        directory: Caminho do diretório para formatar
        check_types: Se True, executa verificação de tipos com MyPy
        max_attempts: Número máximo de tentativas de formatação

    Returns:
        True se todas as verificações passaram
    """
    current_errors: list[str] = []

    for attempt in range(1, max_attempts + 1):
        if attempt > 1:
            console.print(f"\n[yellow]Tentativa {attempt} de {max_attempts}...[/yellow]")

        # Executa Ruff com correções
        passed_ruff, ruff_errors = run_ruff(directory, fix=True)
        current_errors = ruff_errors

        if passed_ruff:
            # Se Ruff passou, verifica tipos com MyPy
            if check_types:
                passed_mypy, mypy_errors = run_mypy(directory)
                if passed_mypy:
                    return True
                current_errors.extend(mypy_errors)
            else:
                return True

    # Se chegou aqui, todas as tentativas falharam
    console.print("\n[red]❌ Erros encontrados após todas as tentativas:[/red]")
    for error in current_errors:
        console.print(f"[red]{error}[/red]")
    return False


def get_python_files(directory: str) -> list[Path]:
    """Retorna lista de arquivos Python em um diretório.

    Args:
        directory: Caminho do diretório para buscar

    Returns:
        Lista de caminhos de arquivos Python
    """
    return list(Path(directory).rglob("*.py"))


def main() -> None:
    """Função principal do script."""
    # Configuração inicial
    directory = "."
    check_types = Confirm.ask(
        "Quer verificar a cobertura de tipos com MyPy?",
        default=True,
    )

    # Conta arquivos Python
    python_files = get_python_files(directory)
    file_count = len(python_files)

    if not file_count:
        console.print("[yellow]⚠️ Nenhum arquivo Python encontrado![/yellow]")
        return

    # Mostra resumo
    title = "🔍 Formatação com Ruff"
    if check_types:
        title += " e MyPy"

    content = [
        f"1. Diretório: {directory}",
        f"2. Arquivos Python encontrados: {file_count}",
        "3. Quer verificar a cobertura de tipos com MyPy?\n",
        "   ✓ Sim" if check_types else "   ✗ Não",
    ]

    console.print(Panel(
        "\n".join(content),
        title=title,
        border_style="blue",
    ))

    if not Confirm.ask("Continuar?", default=True):
        return

    # Executa formatação
    with console.status("[bold blue]Formatando código..."):
        success = format_directory(directory, check_types)

    if success:
        console.print("[green]✅ Todas as verificações passaram![/green]")
    else:
        console.print("[red]❌ Algumas verificações falharam.[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
