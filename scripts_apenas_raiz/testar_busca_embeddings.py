#!/usr/bin/env python3
import os

from sentence_transformers import SentenceTransformer
from supabase import create_client

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_semantic_search(query: str, k: int = 4, threshold: float = 0.5):
    """Testa a busca semântica usando embeddings.

    Args:
        query: A consulta a ser realizada
        k: Número de resultados a retornar (default: 4)
        threshold: Limiar de similaridade (default: 0.5)
    """
    print("\nTestando busca semântica:")
    print(f"Query: {query}")
    print(f"K: {k}")
    print(f"Threshold: {threshold}")
    print(f"URL: {SUPABASE_URL}")

    try:
        # Inicializa o cliente Supabase
        print("\nInicializando cliente Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Cliente inicializado com sucesso!")

        # Inicializa o modelo de embeddings
        print("\nInicializando modelo de embeddings...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Modelo inicializado com sucesso!")

        # Gera embedding da query
        print("\nGerando embedding da query...")
        query_embedding = model.encode(query).tolist()
        print("Embedding gerado com sucesso!")

        # Busca documentos similares
        print("\nBuscando documentos similares...")
        results = supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": k,
                "match_threshold": threshold
            }
        ).execute()

        if results.data:
            print(f"\nResultados encontrados: {len(results.data)}")
            print("\nDetalhes dos resultados:")
            for i, doc in enumerate(results.data, 1):
                print(f"\nResultado {i}:")
                print(f"ID: {doc.get('id')}")
                print(f"Conteúdo: {doc.get('content')[:200]}...")  # Mostra apenas os primeiros 200 caracteres
                print(f"Metadados: {doc.get('metadata')}")
                if "similarity" in doc:
                    print(f"Similaridade: {doc.get('similarity'):.4f}")
        else:
            print("\nNenhum resultado encontrado via busca semântica")

            # Tenta busca simples como fallback
            print("\nTentando busca simples como fallback...")
            docs = supabase.table("documents").select("*").ilike("content", f"%{query}%").limit(k).execute()

            if docs.data:
                print(f"\nResultados encontrados (busca simples): {len(docs.data)}")
                for i, doc in enumerate(docs.data, 1):
                    print(f"\nResultado {i}:")
                    print(f"ID: {doc.get('id')}")
                    print(f"Conteúdo: {doc.get('content')[:200]}...")
                    print(f"Metadados: {doc.get('metadata')}")
            else:
                print("Nenhum resultado encontrado")

    except Exception as e:
        print(f"\nErro na busca: {e!s}")

if __name__ == "__main__":
    # Verifica configuração
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Erro: SUPABASE_URL e SUPABASE_KEY devem estar definidos nas variáveis de ambiente")
        exit(1)

    # Testa com diferentes queries e thresholds
    test_cases = [
        # Queries específicas para as regras
        ("Regras do Docker", 4, 0.5),
        ("Configuração do Supabase", 4, 0.5),
        ("Logs e monitoramento", 4, 0.5),
        ("Arquivos críticos", 4, 0.5)
    ]

    for query, k, threshold in test_cases:
        test_semantic_search(query, k, threshold)
        print("\n" + "="*50 + "\n")
