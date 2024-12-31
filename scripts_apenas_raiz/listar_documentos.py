#!/usr/bin/env python3
from dotenv import load_dotenv
from supabase import create_client

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Supabase
SUPABASE_URL = "https://uaxnbpzamzxradpmccse.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVheG5icHphbXp4cmFkcG1jY3NlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzYyNjkzOSwiZXhwIjoyMDQ5MjAyOTM5fQ.gaXXpBWN26TZ1wTcLGrEBKaKG7dsc5JNDBAIRvOhwY0"

def list_documents():
    """Lista todos os documentos no Supabase."""
    try:
        # Inicializa o cliente Supabase
        print("\nInicializando cliente Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Cliente inicializado com sucesso!")

        # Lista todos os documentos
        print("\nListando documentos:")
        docs = supabase.table("documents").select("*").execute()

        if docs.data:
            print(f"\nTotal de documentos: {len(docs.data)}")
            for i, doc in enumerate(docs.data, 1):
                print(f"\nDocumento {i}:")
                print(f"ID: {doc.get('id')}")
                print(f"Content: {doc.get('content')[:200]}...")  # Mostra apenas os primeiros 200 caracteres
                print(f"Metadata: {doc.get('metadata')}")
                print(f"Embedding ID: {doc.get('embedding_id')}")
                print(f"Created At: {doc.get('created_at')}")
                print(f"Updated At: {doc.get('updated_at')}")
                print(f"Document Hash: {doc.get('document_hash')}")
        else:
            print("Nenhum documento encontrado")

    except Exception as e:
        print(f"\nErro ao listar documentos: {e!s}")

if __name__ == "__main__":
    list_documents()
