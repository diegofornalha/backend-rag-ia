#!/usr/bin/env python3
"""
Ferramenta CLI para fazer upload de documentos para o Supabase.
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def verificar_tabela(supabase: Client) -> bool:
    """Verifica se a tabela existe no Supabase."""
    try:
        # Verifica se a tabela existe usando RPC
        result = supabase.rpc('executar_sql', {
            'sql': """
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'rag'
                AND table_name = '01_base_conhecimento_regras_geral'
            )
            """
        }).execute()
        
        if not result.data or not result.data[0]['exists']:
            return False
        return True
        
    except Exception as e:
        print(f"\nErro ao verificar tabela: {e}")
        if hasattr(e, 'details'):
            print(f"Detalhes: {e.details}")
        return False

def upload_documentos(supabase: Client) -> None:
    """Faz upload dos documentos para o Supabase."""
    try:
        # Verifica se a tabela existe
        if not verificar_tabela(supabase):
            print("\n❌ Tabela 'rag.01_base_conhecimento_regras_geral' não encontrada no Supabase")
            print("\nExecute primeiro os scripts SQL em sql_apenas_raiz/1_setup/:")
            print("1. a_01_base_conhecimento_regras_geral.sql")
            print("2. b_02_embeddings_regras_geral.sql")
            print("3. c_setup_search.sql")
            return
        
        print("\n✅ Tabela encontrada, iniciando upload...")
        
        # Lista os arquivos na pasta de documentos
        documentos_dir = "documentos"
        if not os.path.exists(documentos_dir):
            print(f"\n❌ Pasta '{documentos_dir}' não encontrada")
            return
        
        arquivos = [f for f in os.listdir(documentos_dir) if f.endswith('.json')]
        if not arquivos:
            print(f"\n❌ Nenhum arquivo .json encontrado em '{documentos_dir}'")
            return
        
        print(f"\nEncontrados {len(arquivos)} arquivos para upload:")
        for arquivo in arquivos:
            print(f"- {arquivo}")
        
        # Processa cada arquivo
        for arquivo in arquivos:
            print(f"\nProcessando {arquivo}...")
            
            # Lê o arquivo
            with open(os.path.join(documentos_dir, arquivo), 'r') as f:
                documento = json.load(f)
            
            try:
                # Insere o documento usando RPC
                result = supabase.rpc('insert_into_rag', {
                    'table_name': '01_base_conhecimento_regras_geral',
                    'data': documento
                }).execute()
                
                print(f"✅ Documento '{arquivo}' inserido com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao inserir documento '{arquivo}': {e}")
                if hasattr(e, 'details'):
                    print(f"Detalhes: {e.details}")
                continue
        
        print("\n✅ Upload concluído!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o upload: {e}")
        if hasattr(e, 'details'):
            print(f"Detalhes: {e.details}")

def main():
    """Função principal."""
    print("\n📤 Upload de Documentos para Supabase")
    
    # Configuração do cliente Supabase
    url: str = os.environ.get("SUPABASE_URL", "")
    key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    
    if not url or not key:
        print("\n❌ Erro: Variáveis de ambiente SUPABASE_URL e/ou SUPABASE_SERVICE_ROLE_KEY não encontradas")
        print("\nVerifique se as variáveis estão definidas no arquivo .env:")
        print("SUPABASE_URL=<sua_url>")
        print("SUPABASE_SERVICE_ROLE_KEY=<sua_chave>")
        return
    
    try:
        # Conecta ao Supabase
        supabase: Client = create_client(url, key)
        upload_documentos(supabase)
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar com Supabase: {e}")
        if hasattr(e, 'message'):
            print(f"Detalhes: {e.message}")

if __name__ == "__main__":
    main()