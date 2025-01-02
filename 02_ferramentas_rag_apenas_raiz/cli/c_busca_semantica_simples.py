#!/usr/bin/env python3
"""
Busca semântica simples.
"""

import json
import os
from contextlib import contextmanager
from typing import Any

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

# Carrega variáveis de ambiente
load_dotenv()

# Configura console
console = Console()

def get_api_url(endpoint: str = "") -> str:
    """
    Constrói a URL da API.
    
    Args:
        endpoint: Endpoint da API (opcional)
        
    Returns:
        str: URL completa da API
    """
    base_url = os.getenv("ACTIVE_URL", os.getenv("LOCAL_URL", "http://localhost:10000"))
    api_version = os.getenv("API_VERSION", "v1")
    base = f"{base_url}/api/{api_version}"
    return f"{base}/{endpoint.lstrip('/')}" if endpoint else base

@contextmanager
def search_spinner(text: str = "Buscando..."):
    """Mostra um spinner durante a busca."""
    with console.status(text) as status:
        try:
            yield status
        finally:
            status.stop()

def search_documents(query: str) -> dict[str, Any] | None:
    """Realiza busca semântica via API.
    
    Args:
        query: Termo de busca
        
    Returns:
        Resultados da busca ou None se houver erro
    """
    try:
        # Constrói endpoint de busca
        search_endpoint = get_api_url("search")
        
        # Faz requisição para a API
        response = requests.post(
            search_endpoint,
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        # Verifica se a requisição foi bem sucedida
        response.raise_for_status()
        
        # Processa resultado
        try:
            data = response.json()
            
            # Verifica formato e ajusta se necessário
            if isinstance(data, dict):
                if "results" in data:
                    # Formato esperado
                    return data
                else:
                    # Encapsula em results se necessário
                    return {"results": data}
            else:
                console.print("\n[yellow]Aviso: Formato de resposta inesperado[/yellow]")
                return None
                
        except json.JSONDecodeError:
            console.print("\n[red]Erro ao decodificar resposta da API[/red]")
            return None
        
    except requests.exceptions.RequestException as e:
        console.print("\n[red]Erro ao conectar com a API: %s[/red]", str(e))
        console.print("\n[yellow]Tentando conectar em: %s[/yellow]", search_endpoint)
        return None
    except Exception as e:
        console.print("\n[red]Erro inesperado: %s[/red]", str(e))
        return None

def format_results(results: dict[str, Any]) -> None:
    """Formata e exibe os resultados da busca.
    
    Args:
        results: Dicionário com resultados da busca
    """
    docs = results.get("results", [])
    
    if not docs:
        console.print("\n[yellow]Nenhum documento encontrado[/yellow]")
        return
        
    console.print(f"\n[bold]Documentos encontrados ({len(docs)}):[/bold]")
    
    # Cria tabela
    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Título")
    table.add_column("Relevância", justify="right")
    
    # Adiciona resultados
    for doc in docs:
        similarity = doc.get("similarity", 0)
        table.add_row(
            str(doc.get("id", ""))[:10],
            doc.get("titulo", ""),
            f"{similarity*100:.0f}%"
        )
        
    console.print(table)

def main() -> None:
    """Função principal."""
    try:
        console.print("\n[bold]🔍 Busca Semântica[/bold]")
        console.print("Digite 'sair' para encerrar.")
        
        while True:
            # Obtém query do usuário
            query = Prompt.ask("\n[bold]Buscar por[/bold]")
            
            if query.lower() == "sair":
                console.print("\n[bold]👋 Até logo![/bold]")
                break
                
            with search_spinner():
                # Realiza busca
                results = search_documents(query)
                
                if results:
                    # Formata e exibe resultados
                    format_results(results)
                else:
                    console.print("\n[red]❌ Não foi possível realizar a busca[/red]")
                
    except KeyboardInterrupt:
        console.print("\n\n[bold]👋 Até logo![/bold]")
    except Exception as e:
        console.print("\n[red]Erro inesperado: %s[/red]", str(e))

if __name__ == "__main__":
    main() 