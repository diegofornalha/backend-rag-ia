import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega variáveis de ambiente
load_dotenv()

def verificar_tabelas(supabase: Client) -> None:
    """Verifica a estrutura das tabelas no schema rag."""
    print("\n🔍 Verificando estrutura das tabelas no schema rag...")
    
    try:
        # Verifica se o schema rag existe
        result = supabase.rpc('executar_sql', {
            'sql': """
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'rag'
            """
        }).execute()
        
        if not result.data:
            print("\n❌ Schema 'rag' não encontrado!")
            return
        
        print("\n✅ Schema 'rag' encontrado")
        
        # Lista todas as tabelas no schema rag
        result = supabase.rpc('executar_sql', {
            'sql': """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'rag'
            ORDER BY table_name, ordinal_position
            """
        }).execute()
        
        if not result.data:
            print("\n❌ Nenhuma tabela encontrada no schema 'rag'!")
            return
        
        # Organiza os resultados por tabela
        tabelas = {}
        for row in result.data:
            table_name = row['table_name']
            if table_name not in tabelas:
                tabelas[table_name] = []
            tabelas[table_name].append({
                'coluna': row['column_name'],
                'tipo': row['data_type'],
                'nullable': row['is_nullable']
            })
        
        # Exibe informações de cada tabela
        for table_name, colunas in tabelas.items():
            print(f"\n📋 Tabela: {table_name}")
            print("Colunas:")
            for col in colunas:
                nullable = "NULL" if col['nullable'] == 'YES' else 'NOT NULL'
                print(f"  - {col['coluna']}: {col['tipo']} {nullable}")
        
    except Exception as e:
        print(f"\n❌ Erro ao verificar tabelas: {e}")
        if hasattr(e, 'message'):
            print(f"Detalhes: {e.message}")

def main():
    """Função principal."""
    print("\n🔍 Verificador de Tabelas no Supabase")
    
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
        verificar_tabelas(supabase)
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar com Supabase: {e}")
        if hasattr(e, 'message'):
            print(f"Detalhes: {e.message}")

if __name__ == "__main__":
    main() 