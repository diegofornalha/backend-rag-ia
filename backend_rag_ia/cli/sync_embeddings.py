#!/usr/bin/env python3

import os
import time
from typing import Any

from dotenv import load_dotenv
from rich.console import Console
from sentence_transformers import SentenceTransformer
from supabase import Client, create_client

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


def get_documents_without_embeddings(supabase: Client) -> list[dict[str, Any]]:
    """Obtém documentos que não possuem embeddings."""
    try:
        # Primeiro obtém os IDs dos documentos que já têm embeddings
        embeddings_response = (
            supabase.table("02_embeddings_regras_geral")
            .select("documento_id")
            .execute()
        )
        
        # Extrai os IDs dos documentos que já têm embeddings
        docs_with_embeddings = [doc["documento_id"] for doc in embeddings_response.data]
        
        # Busca documentos que não têm embeddings
        if docs_with_embeddings:
            response = (
                supabase.table("01_base_conhecimento_regras_geral")
                .select("id, conteudo")
                .not_("id", "in", f"({','.join(map(str, docs_with_embeddings))})")
                .execute()
            )
        else:
            # Se não houver embeddings, retorna todos os documentos
            response = (
                supabase.table("01_base_conhecimento_regras_geral")
                .select("id, conteudo")
                .execute()
            )

        documents = response.data
        console.print(f"\n🔍 Encontrados {len(documents)} documentos sem embeddings.")

        return documents

    except Exception as e:
        console.print(f"❌ Erro ao buscar documentos: {e}")
        return []


def create_embedding(content: str) -> list[float]:
    """Cria embedding para o conteúdo usando o modelo."""
    try:
        embedding = model.encode(content)
        return embedding.tolist()
    except Exception as e:
        console.print(f"❌ Erro ao criar embedding: {e}")
        return []


def sync_document_embedding(supabase: Client, document: dict[str, Any]) -> bool:
    """Sincroniza o embedding de um documento."""
    try:
        doc_id = document["id"]
        content = document["conteudo"]

        # Cria embedding
        embedding = create_embedding(content)
        if not embedding:
            return False

        # Insere embedding
        data = {"documento_id": doc_id, "embedding": embedding}

        console.print(f"📤 Sincronizando embedding para documento {doc_id}...")
        result = supabase.table("02_embeddings_regras_geral").insert(data).execute()

        if result.data:
            console.print("✅ Embedding sincronizado com sucesso!")
            return True

        console.print("❌ Erro ao sincronizar embedding")
        if hasattr(result, "error"):
            console.print(f"📝 Erro: {result.error}")
        return False

    except Exception as e:
        console.print(f"❌ Erro ao sincronizar embedding: {e}")
        return False


def main():
    """Função principal."""
    console.print("🔄 Iniciando sincronização de embeddings...")

    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return

    console.print("✅ Conectado ao Supabase!")

    # Obtém documentos sem embeddings
    documents = get_documents_without_embeddings(supabase)
    if not documents:
        console.print("✨ Todos os documentos já possuem embeddings!")
        return

    console.print(f"\n🔍 Encontrados {len(documents)} documentos sem embeddings.")

    # Processa cada documento
    start_time = time.time()
    sucessos = 0
    falhas = 0

    for doc in documents:
        if sync_document_embedding(supabase, doc):
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # Espera 1 segundo entre sincronizações

    # Estatísticas finais
    tempo_total = time.time() - start_time
    console.print(f"\nSincronização concluída em {tempo_total:.2f} segundos!")
    if sucessos > 0:
        console.print(f"✅ {sucessos} embeddings sincronizados com sucesso")
    if falhas > 0:
        console.print(f"❌ {falhas} embeddings falharam")


if __name__ == "__main__":
    main()
