"""
Script para verificar o status das funções RPC no Supabase.
"""
import os

import requests
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_headers(key):
    """Retorna os headers para a requisição"""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def check_function_exists(function_name):
    """Verifica se uma função existe no Supabase"""
    print(f"\n🔍 Verificando função {function_name}...")
    try:
        # Consulta para verificar se a função existe
        query = f"""
        SELECT 
            p.proname as function_name,
            pg_get_functiondef(p.oid) as definition,
            r.rolname as owner,
            n.nspname as schema
        FROM pg_proc p
        JOIN pg_roles r ON p.proowner = r.oid
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE p.proname = '{function_name}'
        """
        
        url = f"{SUPABASE_URL}/rest/v1/rpc/executar_sql"
        response = requests.post(
            url,
            headers=get_headers(SERVICE_KEY),
            json={"sql": query}
        )
        response.raise_for_status()
        result = response.json()
        
        if result:
            print(f"✅ Função {function_name} encontrada")
            print(f"👤 Owner: {result[0].get('owner')}")
            print(f"📁 Schema: {result[0].get('schema')}")
            print("\n📝 Definição:")
            print(result[0].get('definition'))
            return True
        else:
            print(f"❌ Função {function_name} não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar função: {e!s}")
        return False

def check_table_exists(schema, table_name):
    """Verifica se uma tabela existe no Supabase"""
    print(f"\n🔍 Verificando tabela {schema}.{table_name}...")
    try:
        query = f"""
        SELECT 
            table_schema,
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = '{schema}'
        AND table_name = '{table_name}'
        ORDER BY ordinal_position;
        """
        
        url = f"{SUPABASE_URL}/rest/v1/rpc/executar_sql"
        response = requests.post(
            url,
            headers=get_headers(SERVICE_KEY),
            json={"sql": query}
        )
        response.raise_for_status()
        result = response.json()
        
        if result:
            print(f"✅ Tabela {schema}.{table_name} encontrada")
            print("\n📝 Colunas:")
            for col in result:
                print(f"- {col['column_name']}: {col['data_type']} ({col['is_nullable']})")
            return True
        else:
            print(f"❌ Tabela {schema}.{table_name} não encontrada")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabela: {e!s}")
        return False

def main():
    """Função principal"""
    print("\n🔧 Verificando status das funções RPC no Supabase\n")
    
    # Verificar tabelas
    tables = [
        ("rag", "01_base_conhecimento_regras_geral"),
        ("rag", "02_embeddings_regras_geral")
    ]
    
    print("\n📊 Verificando tabelas...")
    for schema, table in tables:
        check_table_exists(schema, table)
    
    # Lista de funções para verificar
    functions = [
        "select_from_rag",
        "insert_into_rag",
        "update_in_rag",
        "delete_from_rag",
        "executar_sql"
    ]
    
    # Verificar cada função
    print("\n📊 Verificando funções...")
    results = {}
    for func in functions:
        results[func] = check_function_exists(func)
    
    # Resumo
    print("\n📊 Resumo:")
    for func, exists in results.items():
        print(f"{func}: {'✅' if exists else '❌'}")

if __name__ == "__main__":
    main() 