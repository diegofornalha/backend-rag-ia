#!/usr/bin/env python3
import glob
import os
import subprocess

from rich.console import Console
from rich.panel import Panel

console = Console()


def check_directory_references():
    """Verifica referências a diretórios em todos os arquivos Python."""
    try:
        console.print(
            Panel.fit("🔍 Verificando referências a diretórios", style="bold yellow")
        )

        # Mapeamento de diretórios antigos para novos
        dir_mapping = {
            "backend-rag-ia": "backend_rag_ia",
            "scripts": "scripts_apenas_raiz",
            "tests": "tests_apenas_raiz",
        }

        # Procura em todos os arquivos Python
        python_files = glob.glob("**/*.py", recursive=True)

        issues_found = False
        for file_path in python_files:
            with open(file_path) as f:
                content = f.read()

            for old_dir, new_dir in dir_mapping.items():
                if old_dir in content:
                    console.print(
                        f"[red]⚠️ Arquivo {file_path} contém referência ao diretório antigo '{old_dir}'[/red]"
                    )
                    console.print(
                        f"[yellow]   Sugestão: Atualizar para '{new_dir}'[/yellow]"
                    )
                    issues_found = True

        if not issues_found:
            console.print(
                "[green]✅ Nenhuma referência desatualizada encontrada![/green]"
            )

        return not issues_found

    except Exception as e:
        console.print(f"[red]❌ Erro ao verificar referências: {e!s}[/red]")
        return False


def run_black(directory: str) -> bool:
    """Executa o Black em um diretório.

    Args:
        directory: Caminho do diretório para formatar.

    Returns:
        bool: True se a formatação foi bem sucedida, False caso contrário.
    """
    try:
        result = subprocess.run(
            ["black", directory], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]❌ Erro ao executar Black: {e!s}[/red]")
        return False


def run_ruff(directory: str) -> tuple[bool, list[str]]:
    """Executa o Ruff em um diretório e retorna os problemas encontrados.

    Args:
        directory: O diretório a ser verificado.

    Returns:
        Uma tupla contendo:
        - bool: True se passou na verificação, False caso contrário
        - list[str]: Lista de erros encontrados
    """
    try:
        result = subprocess.run(
            [
                "ruff",
                "check",
                directory,
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            console.print(f"[green]✅ {directory} passou na verificação do Ruff![/green]")
            return True, []

        errors = result.stdout.splitlines()
        return False, errors

    except Exception as e:
        console.print(f"[red]❌ Erro ao executar Ruff: {e!s}[/red]")
        return False, [str(e)]


def format_and_check_directory(directory: str, max_attempts: int = 3) -> bool:
    """Formata e verifica um diretório, tentando corrigir problemas automaticamente.

    Args:
        directory: Caminho do diretório para processar.
        max_attempts: Número máximo de tentativas de correção.

    Returns:
        bool: True se todas as verificações passaram, False caso contrário.
    """
    if not os.path.exists(directory):
        console.print(f"[yellow]⚠️ Diretório {directory} não encontrado[/yellow]")
        return False

    attempt = 1
    last_errors = []
    
    while attempt <= max_attempts:
        console.print(f"\n[cyan]Tentativa {attempt} de {max_attempts} para {directory}...[/cyan]")
        
        # Executa Black
        if not run_black(directory):
            console.print(f"[red]❌ Black falhou na tentativa {attempt}[/red]")
            return False
        
        # Executa Ruff
        passed, current_errors = run_ruff(directory)
        if passed:
            console.print(f"[green]✅ Todas as verificações passaram para {directory}![/green]")
            return True
        
        # Verifica se os erros são os mesmos da última tentativa
        if set(current_errors) == set(last_errors):
            console.print("[yellow]⚠️ Mesmos erros persistem, interrompendo tentativas[/yellow]")
            break
        
        last_errors = current_errors
        attempt += 1
    
    console.print(f"[red]❌ Não foi possível corrigir todos os problemas em {directory} após {max_attempts} tentativas[/red]")
    return False


def format_python_files():
    """Formata todos os arquivos Python do projeto usando Black e verifica com Ruff."""
    try:
        # Primeiro verifica referências
        check_directory_references()

        # Lista de diretórios para formatar
        directories = ["backend_rag_ia", "monitoring", "scripts_apenas_raiz"]

        # Formatação e verificação
        console.print(
            Panel.fit("🎨 Formatando e verificando código Python", style="bold blue")
        )

        all_passed = True
        for directory in directories:
            if not format_and_check_directory(directory):
                all_passed = False

        if all_passed:
            console.print(
                "\n[bold green]✨ Formatação e verificação concluídas com sucesso![/bold green]"
            )
        else:
            console.print(
                "\n[bold yellow]⚠️ Formatação concluída, mas alguns problemas persistem[/bold yellow]"
            )

    except Exception as e:
        console.print(f"[red]❌ Erro durante o processo: {e!s}[/red]")
        return False

    return True


if __name__ == "__main__":
    format_python_files()
