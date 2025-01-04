#!/usr/bin/env python3
import os
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

console = Console()

def check_environment():
    """Verifica as variáveis de ambiente necessárias."""
    env_vars = {
        "SEMANTIC_SEARCH_MODE": os.getenv("SEMANTIC_SEARCH_MODE", "local"),
        "RENDER_API_KEY": "✓ Configurado" if os.getenv("RENDER_API_KEY") else "✗ Não configurado",
        "RENDER_SERVICE_ID": os.getenv("RENDER_SERVICE_ID", "Não configurado")
    }

    table = Table(title="Variáveis de Ambiente")
    table.add_column("Variável", style="cyan")
    table.add_column("Valor", style="green")

    for var, value in env_vars.items():
        # Mascara a chave API se estiver presente
        if var == "RENDER_API_KEY" and os.getenv("RENDER_API_KEY"):
            masked_key = os.getenv("RENDER_API_KEY")[:8] + "..." + os.getenv("RENDER_API_KEY")[-4:]
            table.add_row(var, "✓ " + masked_key)
        else:
            table.add_row(var, str(value))

    return table

def check_endpoints():
    """Verifica a configuração dos endpoints."""
    table = Table(title="Endpoints Configurados")
    table.add_column("Modo", style="cyan")
    table.add_column("URL", style="yellow")
    table.add_column("Ambiente", style="green")

    local_url = os.getenv("SEMANTIC_SEARCH_LOCAL_URL", "http://localhost:8000/search")
    render_url = os.getenv("SEMANTIC_SEARCH_RENDER_URL", "https://api.coflow.com.br/search")
    os.getenv("ENVIRONMENT", "local")

    table.add_row("Local", local_url, "Development")
    table.add_row("Render", render_url, "Production")

    return table

def check_status():
    """Verifica o status atual do sistema."""
    table = Table(title="Status do Sistema")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="yellow")

    mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
    environment = os.getenv("ENVIRONMENT", "local")

    table.add_row("Modo Atual", mode)
    table.add_row("Ambiente", environment)
    table.add_row("Modos Disponíveis", "local, render, auto")

    return table

def main():
    """Exibe um relatório do status da busca semântica."""
    console.print("\n[bold]📊 Relatório de Status da Busca Semântica[/bold]\n")

    # Verifica ambiente
    console.print("\n[cyan]Configuração do Ambiente:[/cyan]")
    console.print(check_environment())

    # Verifica endpoints
    console.print("\n[cyan]Endpoints Configurados:[/cyan]")
    console.print(check_endpoints())

    # Verifica status
    console.print("\n[cyan]Status do Sistema:[/cyan]")
    console.print(check_status())

    # Timestamp
    console.print(f"\n[dim]Relatório gerado em: {datetime.now().isoformat()}[/dim]")

if __name__ == "__main__":
    main()
