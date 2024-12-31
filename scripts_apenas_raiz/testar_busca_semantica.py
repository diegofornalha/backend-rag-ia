#!/usr/bin/env python3
import asyncio
import os
from rich.console import Console
from backend_rag_ia.services.semantic_search import SemanticSearchManager

console = Console()

async def test_search(query: str, mode: str):
    """Testa a busca semântica em um modo específico."""
    os.environ["SEMANTIC_SEARCH_MODE"] = mode
    manager = SemanticSearchManager()
    
    console.print(f"\n[cyan]Testando busca no modo {mode}[/cyan]")
    console.print(f"Query: {query}")
    
    try:
        results = await manager.search(query)
        console.print("[green]✓ Busca realizada com sucesso![/green]")
        console.print("Resultados:", results)
        
        status = manager.get_status()
        console.print("\nStatus:", status)
        
    except Exception as e:
        console.print(f"[red]✗ Erro na busca: {str(e)}[/red]")
        
        status = manager.get_status()
        console.print("\nStatus após erro:", status)

async def main():
    """Executa testes em diferentes modos."""
    query = "Como implementar busca semântica em Python?"
    
    # Testa cada modo
    for mode in ["local", "render", "auto"]:
        await test_search(query, mode)
        await asyncio.sleep(1)  # Pequena pausa entre testes

if __name__ == "__main__":
    console.print("[bold]🔍 Iniciando testes de busca semântica[/bold]")
    asyncio.run(main()) 