#!/usr/bin/env python3
import subprocess
import os
from rich.console import Console
from rich.panel import Panel

console = Console()


def format_python_files():
    """Formata todos os arquivos Python do projeto usando Black."""
    try:
        # Lista de diretórios para formatar
        directories = ["backend-rag-ia", "monitoring", "scripts", "tests"]

        console.print(
            Panel.fit("🎨 Formatando código Python com Black", style="bold blue")
        )

        for directory in directories:
            if os.path.exists(directory):
                console.print(f"\n[cyan]Formatando arquivos em {directory}...[/cyan]")
                result = subprocess.run(
                    ["black", directory], capture_output=True, text=True
                )

                if result.returncode == 0:
                    console.print(
                        f"[green]✅ {directory} formatado com sucesso![/green]"
                    )
                else:
                    console.print(f"[red]❌ Erro ao formatar {directory}:[/red]")
                    console.print(result.stderr)
            else:
                console.print(
                    f"[yellow]⚠️ Diretório {directory} não encontrado[/yellow]"
                )

        console.print("\n[bold green]✨ Formatação concluída![/bold green]")

    except Exception as e:
        console.print(f"[red]❌ Erro durante a formatação: {str(e)}[/red]")
        return False

    return True


if __name__ == "__main__":
    format_python_files()
