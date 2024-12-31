#!/usr/bin/env python3

import os

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from supabase.client import create_client

load_dotenv()
console = Console()

def check_supabase():
    """Verifica os dados no Supabase."""
    try:
        # Conexão com Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

        # Verifica documentos
        docs = supabase.table("documents").select("*").execute()
        console.print(f"\n📚 Documentos encontrados: {len(docs.data)}")

        if docs.data:
            table = Table()
            table.add_column("ID")
            table.add_column("Título")
            table.add_column("Conteúdo", max_width=50)

            for doc in docs.data:
                title = doc.get("metadata", {}).get("title", "N/A")
                content = doc.get("content", "")[:47] + "..." if doc.get("content") else "N/A"
                table.add_row(str(doc["id"]), title, content)

            console.print(table)

        # Verifica embeddings
        embeddings = supabase.table("embeddings").select("*").execute()
        console.print(f"\n🧠 Embeddings encontrados: {len(embeddings.data)}")

        if embeddings.data:
            table = Table()
            table.add_column("ID")
            table.add_column("Document ID")
            table.add_column("Dimensões")

            for emb in embeddings.data:
                dims = len(emb["embedding"]) if emb.get("embedding") else 0
                table.add_row(str(emb["id"]), str(emb["document_id"]), str(dims))

            console.print(table)

    except Exception as e:
        console.print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_supabase()
