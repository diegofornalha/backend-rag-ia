#!/usr/bin/env python3
import os

import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_render_search(query: str, k: int = 4):
    """Testa a busca semântica no Render.

    Args:
        query: A consulta a ser realizada
        k: Número de resultados a retornar (default: 4)
    """
    base_url = os.getenv("SEMANTIC_SEARCH_RENDER_URL", "https://api.coflow.com.br")
    render_api_key = os.getenv("RENDER_API_KEY")

    # Constrói a URL completa
    render_url = f"{base_url}/api/v1/search"

    if not render_api_key:
        print("Erro: RENDER_API_KEY não configurada")
        return

    print("\nTestando busca no Render:")
    print(f"Query: {query}")
    print(f"K: {k}")
    print(f"URL: {render_url}")

    try:
        response = requests.post(
            render_url,
            json={
                "query": query,
                "k": k
            },
            headers={
                "Authorization": f"Bearer {render_api_key}",
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            timeout=10.0
        )
        response.raise_for_status()
        results = response.json()

        print("\nResultados:")
        print("Status: Sucesso")
        print(f"Resultados encontrados: {len(results.get('results', []))}")
        print(f"Count: {results.get('count', 0)}")

        if results.get("results"):
            print("\nDetalhes dos resultados:")
            for i, result in enumerate(results["results"], 1):
                print(f"\nResultado {i}:")
                print(result)

    except Exception as e:
        print(f"\nErro na busca: {e!s}")
        if hasattr(e, "response"):
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            print(f"Headers: {e.response.headers}")

if __name__ == "__main__":
    # Testa com diferentes queries
    queries = [
        "Como implementar autenticação JWT?",
        "FastAPI documentação",
        "PostgreSQL pgvector",
        "Render deploy"
    ]

    for query in queries:
        test_render_search(query, k=4)
        print("\n" + "="*50 + "\n")
