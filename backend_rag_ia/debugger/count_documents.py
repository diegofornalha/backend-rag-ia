#!/usr/bin/env python3

import json
import os
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from supabase import Client, create_client

load_dotenv()

console = Console()


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


def get_documents_count(supabase: Client) -> dict[str, Any]:
    """Obtém a contagem e lista de documentos."""
    try:
        # Busca documentos na tabela documents
        response = supabase.table("documents").select("*").execute()
        documents = response.data

        # Debug do formato dos documentos
        console.print("\n🔍 Formato dos documentos:")
        console.print(
            json.dumps(documents[:2], indent=2)
        )  # Mostra apenas 2 para não poluir

        return {"count": len(documents), "documents": documents}
    except Exception as e:
        console.print(f"❌ Erro ao buscar documentos: {e}")
        return {"count": 0, "documents": []}


def display_documents_table(documents: list):
    """Exibe uma tabela formatada com os documentos."""
    table = Table(title="Documentos no Supabase")

    table.add_column("ID", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("Título", style="green")
    table.add_column("Conteúdo", style="yellow", max_width=50)

    for doc in documents:
        content = doc.get("content", "N/A")
        metadata = doc.get("metadata", {})

        # Limita o tamanho do conteúdo
        if len(content) > 47:
            content = content[:47] + "..."

        table.add_row(
            str(doc.get("id", "N/A")),
            metadata.get("type", "N/A"),
            metadata.get("title", "N/A"),
            content,
        )

    console.print(table)


def main():
    """Função principal."""
    console.print("🔍 Verificando documentos no Supabase...")

    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return

    console.print("✅ Conectado ao Supabase!")

    # Obtém os documentos
    result = get_documents_count(supabase)
    count = result["count"]
    documents = result["documents"]

    # Exibe resultados
    console.print(f"\n📊 Total de documentos: {count}")

    if count > 0:
        console.print("\n📝 Lista de documentos:")
        display_documents_table(documents)
    else:
        console.print("\n⚠️ Nenhum documento encontrado!")


if __name__ == "__main__":
    main()
