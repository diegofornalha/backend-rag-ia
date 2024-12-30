import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def test_connection():
    """Testa a conexão com o Supabase."""
    try:
        # Configuração
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            print("Erro: SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")
            return False

        print("\nConectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)

        # Testa a criação das tabelas
        print("\nCriando tabelas...")

        # Tabela documents
        supabase.table("documents").select("*").limit(1).execute()
        print("✓ Tabela 'documents' OK")

        # Tabela embeddings
        supabase.table("embeddings").select("*").limit(1).execute()
        print("✓ Tabela 'embeddings' OK")

        print("\nConexão e tabelas verificadas com sucesso!")
        return True

    except Exception as e:
        print(f"\nErro ao testar conexão: {e!s}")
        return False


if __name__ == "__main__":
    test_connection()
