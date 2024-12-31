#!/usr/bin/env python3
import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

def test_search(query: str) -> dict:
    """Realiza uma busca semântica e retorna os resultados."""
    mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
    local_url = os.getenv("SEMANTIC_SEARCH_LOCAL_URL", "http://localhost:8000/search")
    render_url = os.getenv("SEMANTIC_SEARCH_RENDER_URL", "https://api.coflow.com.br/search")
    render_api_key = os.getenv("RENDER_API_KEY")

    if mode == "auto" or mode == "local":
        try:
            response = requests.post(
                local_url,
                json={"query": query},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if mode == "local":
                raise
            console.print(f"[yellow]Busca local falhou: {e!s}. Tentando Render...[/yellow]")

    if mode == "auto" or mode == "render":
        if not render_api_key:
            raise ValueError("RENDER_API_KEY não configurada")

        response = requests.post(
            render_url,
            json={"query": query},
            headers={"Authorization": f"Bearer {render_api_key}"},
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()

def main():
    """Função principal para executar os testes."""
    console.print("\n[bold]🔍 Teste de Busca Semântica[/bold]\n")

    # Mostra configuração atual
    mode = os.getenv("SEMANTIC_SEARCH_MODE", "local")
    console.print(f"[cyan]Modo:[/cyan] {mode}")

    # Query de teste
    query = "Como implementar autenticação JWT?"
    console.print(f"\n[bold]Query de teste:[/bold] {query}")

    try:
        start_time = datetime.now()
        results = test_search(query)
        duration = (datetime.now() - start_time).total_seconds()

        # Mostra resultados
        table = Table(title="Resultados da Busca")
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="yellow")

        table.add_row("Status", "✓ Sucesso")
        table.add_row("Tempo", f"{duration:.2f}s")
        table.add_row("Resultados Encontrados", str(len(results.get("results", []))))

        console.print("\n[bold]📊 Resultados[/bold]")
        console.print(table)

        # Mostra os resultados detalhados
        if results.get("results"):
            console.print("\n[bold]Detalhes dos Resultados:[/bold]")
            for i, result in enumerate(results["results"], 1):
                console.print(f"\n[cyan]Resultado {i}:[/cyan]")
                console.print(result)

    except Exception as e:
        console.print(f"\n[red]✗ Erro na busca: {e!s}[/red]")

    # Timestamp
    console.print(f"\n[dim]Teste concluído em: {datetime.now().isoformat()}[/dim]")

if __name__ == "__main__":
    main()
