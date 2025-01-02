"""
Script para testar a API direta do Supabase.
"""
import os
from dotenv import load_dotenv
import requests
import json

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def get_headers(key, schema="rag"):
    """Retorna os headers para a requisição"""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation",
        "Accept-Profile": schema,
        "Content-Profile": schema
    }

def test_select_authenticated():
    """Testa SELECT com role authenticated"""
    print("\n🔍 Testando SELECT com role authenticated...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/%2201_base_conhecimento_regras_geral%22"
        params = {"select": "*", "limit": 10}
        response = requests.get(url, headers=get_headers(ANON_KEY), params=params)
        response.raise_for_status()
        result = response.json()
        print("✅ SELECT permitido")
        print(f"Documentos encontrados: {len(result)}")
        return True
    except Exception as e:
        print(f"❌ SELECT negado: {str(e)}")
        return False

def test_insert_authenticated():
    """Testa INSERT com role authenticated"""
    print("\n📝 Testando INSERT com role authenticated...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/%2201_base_conhecimento_regras_geral%22"
        data = {
            "titulo": "Teste Política RLS",
            "conteudo": {"texto": "Teste de inserção com role authenticated"},
            "version_key": "teste_rls_v1",
            "metadata": {"test": True},
            "document_hash": "test_hash",
            "content_hash": "test_content_hash",
            "processing_status": "pending",
            "embedding_attempts": 0
        }
        response = requests.post(url, headers=get_headers(ANON_KEY), json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ INSERT permitido")
        print(f"Documento inserido: {result}")
        return True
    except Exception as e:
        print(f"❌ INSERT negado: {str(e)}")
        return False

def test_update_service_role():
    """Testa UPDATE com service_role"""
    print("\n📝 Testando UPDATE com service_role...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/%2201_base_conhecimento_regras_geral%22"
        params = {"version_key": "eq.teste_rls_v1"}
        data = {
            "titulo": "Teste Atualizado",
            "conteudo": {"texto": "Teste de atualização com role service_role"},
            "metadata": {"test": True, "updated": True},
            "processing_status": "updated"
        }
        response = requests.patch(url, headers=get_headers(SERVICE_KEY), params=params, json=data)
        response.raise_for_status()
        result = response.json()
        print("✅ UPDATE permitido")
        print(f"Documento atualizado: {result}")
        return True
    except Exception as e:
        print(f"❌ UPDATE negado: {str(e)}")
        return False

def test_delete_service_role():
    """Testa DELETE com service_role"""
    print("\n🗑️ Testando DELETE com service_role...")
    try:
        url = f"{SUPABASE_URL}/rest/v1/%2201_base_conhecimento_regras_geral%22"
        params = {"version_key": "eq.teste_rls_v1"}
        response = requests.delete(url, headers=get_headers(SERVICE_KEY), params=params)
        response.raise_for_status()
        result = response.json()
        print("✅ DELETE permitido")
        print(f"Documento deletado: {result}")
        return True
    except Exception as e:
        print(f"❌ DELETE negado: {str(e)}")
        return False

def main():
    """Função principal"""
    print("\n🔧 Testando API direta do Supabase\n")
    
    # Testar operações
    select_ok = test_select_authenticated()
    insert_ok = test_insert_authenticated()
    update_ok = test_update_service_role()
    delete_ok = test_delete_service_role()
    
    # Resumo
    print("\n📊 Resumo dos Testes:")
    print(f"SELECT (authenticated): {'✅' if select_ok else '❌'}")
    print(f"INSERT (authenticated): {'✅' if insert_ok else '❌'}")
    print(f"UPDATE (service_role): {'✅' if update_ok else '❌'}")
    print(f"DELETE (service_role): {'✅' if delete_ok else '❌'}")

if __name__ == "__main__":
    main() 