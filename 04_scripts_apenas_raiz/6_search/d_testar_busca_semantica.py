#!/usr/bin/env python3
import os
from datetime import UTC, datetime

import requests
from rich.console import Console

console = Console()

# URLs dos serviços
LOCAL_URL = os.getenv("SEMANTIC_SEARCH_LOCAL_URL", "http://localhost:10000")
RENDER_URL = os.getenv("SEMANTIC_SEARCH_RENDER_URL", "https://api.coflow.com.br")
SEARCH_MODE = os.getenv("SEMANTIC_SEARCH_MODE", "auto")

def try_local_search(query: str) -> dict:
    """Tenta busca local."""
    response = requests.get(
        f"{LOCAL_URL}/search",
        params={"query": query},
        timeout=10.0
    )
    response.raise_for_status()
    return response.json()

def try_render_search(query: str) -> dict:
    """Tenta busca no Render."""
    response = requests.get(
        f"{RENDER_URL}/search",
        params={"query": query},
        timeout=10.0
    )
    response.raise_for_status()
    return response.json()

def main():
    """Função principal."""
    console.print("\n🔍 Teste de Busca Semântica")
    console.print(f"\nModo: {SEARCH_MODE}")

    # Query de teste
    query = "Como implementar autenticação JWT?"
    console.print(f"\nQuery de teste: {query}")

    try:
        # Tenta busca local primeiro
        if SEARCH_MODE in ["local", "auto"]:
            try:
                results = try_local_search(query)
                console.print("\n✓ Busca local bem sucedida!")
                console.print(f"Resultados: {results}")
                return
            except Exception as e:
                console.print(f"\nBusca local falhou: {e}")
                if SEARCH_MODE == "local":
                    raise

                console.print("Tentando Render...")

        # Tenta Render se local falhou ou modo é render
        if SEARCH_MODE in ["render", "auto"]:
            results = try_render_search(query)
            console.print("\n✓ Busca no Render bem sucedida!")
            console.print(f"Resultados: {results}")
            return

    except Exception as e:
        console.print(f"\n✗ Erro na busca: {e}")

    finally:
        console.print(f"\nTeste concluído em: {datetime.now(UTC).isoformat()}")

if __name__ == "__main__":
    main()
