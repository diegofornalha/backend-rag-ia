#!/usr/bin/env python3

import os
from rich.console import Console
from rich.table import Table
from typing import Dict, Any, List
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer
import sys

load_dotenv()

console = Console()
model = SentenceTransformer("all-MiniLM-L6-v2")


def check_supabase_connection() -> tuple[bool, Client]:
    """Verifica conexão com o Supabase."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            console.print(
                "❌ SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env"
            )
            return False, None

        console.print("\n🔌 Conectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        return True, supabase

    except Exception as e:
        console.print(f"❌ Erro ao conectar ao Supabase: {e}")
        return False, None


def create_embedding(content: str) -> List[float]:
    """Cria embedding para o conteúdo usando o modelo."""
    try:
        embedding = model.encode(content)
        return embedding.tolist()
    except Exception as e:
        console.print(f"❌ Erro ao criar embedding: {e}")
        return []


def search_documents(
    supabase: Client, query: str, limit: int = 3
) -> List[Dict[str, Any]]:
    """Busca documentos similares à query."""
    try:
        # Gera embedding para a query
        query_embedding = create_embedding(query)

        # Busca documentos similares
        response = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.3,
                "match_count": limit,
            },
        ).execute()

        return response.data

    except Exception as e:
        console.print(f"❌ Erro ao buscar documentos: {e}")
        return []


def display_results(documents: List[Dict[str, Any]], query: str):
    """Exibe os resultados da busca."""
    console.print(f"\n🔍 Resultados para: '{query}'")

    if not documents:
        console.print("❌ Nenhum documento encontrado!")
        return

    table = Table()
    table.add_column("Título", style="cyan")
    table.add_column("Relevância", style="magenta")
    table.add_column("Conteúdo", style="green", max_width=60)

    for doc in documents:
        similarity = doc.get("similarity", 0)
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})

        # Limita o tamanho do conteúdo
        if len(content) > 57:
            content = content[:57] + "..."

        table.add_row(metadata.get("title", "N/A"), f"{similarity:.2%}", content)

    console.print(table)


def main():
    """Função principal."""
    if len(sys.argv) < 2:
        console.print("❌ Por favor, forneça uma query para busca!")
        return

    query = " ".join(sys.argv[1:])
    console.print(f"🔍 Buscando: '{query}'")

    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return

    console.print("✅ Conectado ao Supabase!")

    # Busca documentos
    documents = search_documents(supabase, query)

    # Exibe resultados
    display_results(documents, query)


if __name__ == "__main__":
    main()
