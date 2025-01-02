"""Script para testar conexão com Supabase."""

import os
from supabase import create_client

def testar_supabase():
    """Testa conexão com Supabase."""
    # Verifica variáveis de ambiente
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não definidas")
        return False
        
    try:
        # Tenta conectar
        client = create_client(url, key)
        
        # Tenta fazer uma query simples
        response = client.table("rag.documentos").select("id").limit(1).execute()
        
        print("✅ Conexão com Supabase OK")
        print(f"Resposta: {response.data}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False
        
if __name__ == "__main__":
    testar_supabase() 