import hashlib
import json
import os

from dotenv import load_dotenv
from rich import print
from rich.console import Console
from rich.table import Table
from supabase import Client, create_client

# Carrega variáveis de ambiente
load_dotenv()

console = Console()

# Inicializa cliente Supabase com valores padrão caso não encontre no .env
url: str = os.getenv("SUPABASE_URL", "https://xxxxxxxxxxxxxxxxxxxxxx.supabase.co")
key: str = os.getenv(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
supabase: Client = create_client(url, key)


def calculate_content_hash(content: str) -> str:
    """Calcula hash do conteúdo normalizado."""
    normalized = json.dumps(content, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()


def get_all_documents():
    """Recupera todos os documentos do Supabase."""
    response = supabase.table("documents").select("*").execute()
    return response.data


def find_duplicates(documents):
    """Encontra documentos duplicados baseado no conteúdo."""
    content_map = {}
    duplicates = []

    for doc in documents:
        content_hash = calculate_content_hash(doc["content"])
        if content_hash in content_map:
            duplicates.append({"original": content_map[content_hash], "duplicate": doc})
        else:
            content_map[content_hash] = doc

    return duplicates


def remove_duplicate(duplicate_info):
    """Remove o documento duplicado e mantém o original."""
    duplicate_id = duplicate_info["duplicate"]["id"]
    try:
        # Remove primeiro da tabela de embeddings
        supabase.table("embeddings").delete().eq("document_id", duplicate_id).execute()
        # Remove o documento
        supabase.table("documents").delete().eq("id", duplicate_id).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao remover duplicata {duplicate_id}: {e!s}")
        return False


def main():
    console.print("\n🔄 Iniciando sincronização de documentos...\n")

    # Recupera todos os documentos
    documents = get_all_documents()
    console.print(f"📊 Total de documentos encontrados: {len(documents)}")

    # Encontra duplicatas
    duplicates = find_duplicates(documents)
    console.print(f"\n🔍 Encontradas {len(duplicates)} duplicatas")

    if not duplicates:
        console.print("\n✅ Não há duplicatas para remover!")
        return

    # Mostra tabela de duplicatas
    table = Table(title="Documentos Duplicados")
    table.add_column("Original ID")
    table.add_column("Duplicata ID")
    table.add_column("Conteúdo")

    for dup in duplicates:
        table.add_row(
            str(dup["original"]["id"]),
            str(dup["duplicate"]["id"]),
            dup["original"]["content"][:50] + "...",
        )

    console.print(table)

    # Remove duplicatas
    console.print("\n🧹 Removendo duplicatas...")
    removed = 0
    for dup in duplicates:
        if remove_duplicate(dup):
            removed += 1
            console.print(f"✅ Removida duplicata {dup['duplicate']['id']}")

    console.print("\n✨ Sincronização concluída!")
    console.print("📊 Estatísticas finais:")
    console.print(f"   - Total de documentos originais: {len(documents)}")
    console.print(f"   - Duplicatas encontradas: {len(duplicates)}")
    console.print(f"   - Duplicatas removidas: {removed}")
    console.print(f"   - Total após limpeza: {len(documents) - removed}")


if __name__ == "__main__":
    main()
