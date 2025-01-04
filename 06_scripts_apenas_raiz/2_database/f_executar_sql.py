"""
Script para executar SQL via API do Supabase.
"""
import json
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

def execute_sql_file(file_path):
    """Executa um arquivo SQL via API do Supabase"""
    print(f"\n📝 Executando arquivo SQL: {file_path}")
    try:
        # Ler o arquivo SQL
        with open(file_path) as f:
            sql = f.read()
        
        # Dividir o SQL em comandos individuais
        commands = sql.split(';')
        
        # Executar cada comando
        for i, cmd in enumerate(commands, 1):
            # Pular linhas vazias
            cmd = cmd.strip()
            if not cmd:
                continue
            
            print(f"\n🔧 Executando comando {i}...")
            
            # Executar o comando
            url = f"{SUPABASE_URL}/rest/v1/rpc/executar_sql"
            response = requests.post(
                url,
                headers=get_headers(SERVICE_KEY),
                json={"sql": cmd}
            )
            
            # Verificar resposta
            if response.status_code == 200:
                print("✅ Comando executado com sucesso")
                result = response.json()
                if result:
                    print("📊 Resultado:")
                    print(json.dumps(result, indent=2))
            else:
                print(f"❌ Erro ao executar comando: {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ Erro ao executar arquivo SQL: {e!s}")

def main():
    """Função principal"""
    print("\n🔧 Executando scripts SQL no Supabase\n")
    
    # Lista de arquivos SQL para executar
    sql_files = [
        "03_sql_apenas_raiz/1_setup/a_01_base_conhecimento_regras_geral.sql",
        "03_sql_apenas_raiz/1_setup/b_02_embeddings_regras_geral.sql",
        "03_sql_apenas_raiz/2_security/b_policies.sql",
        "03_sql_apenas_raiz/3_migrations/f_setup_rpc.sql"
    ]
    
    # Executar cada arquivo
    for file in sql_files:
        execute_sql_file(file)

if __name__ == "__main__":
    main() 