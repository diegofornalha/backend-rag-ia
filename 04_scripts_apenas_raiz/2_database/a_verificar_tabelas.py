def verificar_tabelas(supabase: Client) -> None:
    """Verifica se as tabelas necessárias existem."""
    try:
        # Verifica tabela de documentos
        response = supabase.table('rag.01_base_conhecimento_regras_geral').select('*').limit(1).execute()
        print("✓ Tabela 'rag.01_base_conhecimento_regras_geral' OK")
        
        # Verifica tabela de embeddings
        response = supabase.table('rag.02_embeddings_regras_geral').select('*').limit(1).execute()
        print("✓ Tabela 'rag.02_embeddings_regras_geral' OK")
        
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        print("\nExecute os scripts SQL em sql_apenas_raiz/1_setup/:")
        print("1. a_01_base_conhecimento_regras_geral.sql")
        print("2. b_02_embeddings_regras_geral.sql") 