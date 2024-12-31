#!/usr/bin/env python3
import os

from dotenv import load_dotenv
from supabase import create_client

# Tenta carregar do .env primeiro
load_dotenv()

# Configuração do Supabase com fallback
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://uaxnbpzamzxradpmccse.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVheG5icHphbXp4cmFkcG1jY3NlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzYyNjkzOSwiZXhwIjoyMDQ5MjAyOTM5fQ.gaXXpBWN26TZ1wTcLGrEBKaKG7dsc5JNDBAIRvOhwY0"

def test_supabase_search(query: str, k: int = 4):
    """Testa a busca no Supabase.

    Args:
        query: A consulta a ser realizada
        k: Número de resultados a retornar (default: 4)
    """
    print("\nTestando busca no Supabase:")
    print(f"Query: {query}")
    print(f"K: {k}")
    print(f"URL: {SUPABASE_URL}")

    try:
        # Inicializa o cliente Supabase
        print("\nInicializando cliente Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Cliente inicializado com sucesso!")

        # Lista as tabelas disponíveis
        print("\nVerificando documentos:")
        tables = supabase.table("documents").select("*").limit(1).execute()
        if tables.data:
            print(f"Estrutura da tabela documents: {tables.data[0].keys()}")
            print(f"Total de documentos encontrados: {len(tables.data)}")
        else:
            print("Tabela documents está vazia")

        # Tenta busca simples
        print("\nBuscando documentos:")
        docs = supabase.table("documents").select("*").ilike("content", f"%{query}%").limit(k).execute()

        if docs.data:
            print(f"\nResultados encontrados: {len(docs.data)}")
            print("\nDetalhes dos resultados:")
            for i, doc in enumerate(docs.data, 1):
                print(f"\nResultado {i}:")
                print(f"ID: {doc.get('id')}")
                print(f"Conteúdo: {doc.get('content')}")
                print(f"Metadados: {doc.get('metadata')}")
        else:
            print("Nenhum resultado encontrado")

    except Exception as e:
        print(f"\nErro na busca: {e!s}")

if __name__ == "__main__":
    # Testa com diferentes queries
    queries = [
        "Como implementar autenticação JWT?",
        "FastAPI documentação",
        "PostgreSQL pgvector",
        "Render deploy"
    ]

    for query in queries:
        test_supabase_search(query, k=4)
        print("\n" + "="*50 + "\n")
