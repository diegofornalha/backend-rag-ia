import os

import requests
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Testa a conexão com o Supabase."""
    try:
        print("\nConectando ao Supabase...")
        service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        supabase_url = os.getenv("SUPABASE_URL", "")
        
        if not service_key or not supabase_url:
            print("\n❌ Credenciais do Supabase não encontradas no .env")
            return False
            
        # Monta a URL da API REST
        api_url = f"{supabase_url}/rest/v1/rpc/select_from_rag"
        
        # Headers necessários
        headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Payload para a função RPC
        payload = {
            "table_name": "01_base_conhecimento_regras_geral",
            "limit_num": 1
        }
        
        print("\nVerificando tabelas...")
        # Faz a requisição direta
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            print("\n✅ Conexão e tabelas OK!")
            print(f"Dados: {response.json()}")
            return True
        else:
            print(f"\n❌ Erro na resposta: {response.text}")
            return False
        
    except Exception as e:
        print(f"\nErro ao testar conexão: {e}")
        return False

if __name__ == "__main__":
    test_connection() 