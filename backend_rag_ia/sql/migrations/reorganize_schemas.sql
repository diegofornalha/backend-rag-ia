-- Verificar tabelas existentes antes de mover
DO $$ 
BEGIN
    RAISE NOTICE 'Tabelas existentes antes da movimentação:';
END $$;

SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Criar os novos schemas
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS rules;

-- Função auxiliar para mover tabelas e suas dependências
CREATE OR REPLACE FUNCTION move_table_with_dependencies(
    p_table_name text,
    p_from_schema text,
    p_to_schema text
) RETURNS void AS $$
DECLARE
    v_exists boolean;
BEGIN
    -- Verificar se a tabela existe
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = p_from_schema
        AND table_name = p_table_name
    ) INTO v_exists;

    IF NOT v_exists THEN
        RAISE NOTICE 'Tabela %.% não existe - pulando', p_from_schema, p_table_name;
        RETURN;
    END IF;

    -- Mover a tabela principal
    EXECUTE format('ALTER TABLE %I.%I SET SCHEMA %I',
        p_from_schema, p_table_name, p_to_schema);
    
    RAISE NOTICE 'Tabela %.% movida com sucesso para schema %',
        p_from_schema, p_table_name, p_to_schema;
END;
$$ LANGUAGE plpgsql;

-- Atualizar permissões nos schemas
GRANT USAGE ON SCHEMA rag TO authenticated;
GRANT USAGE ON SCHEMA rules TO authenticated;

-- Mover tabelas do RAG (apenas as que existem)
DO $$ 
BEGIN
    PERFORM move_table_with_dependencies('documentos', 'public', 'rag');
    PERFORM move_table_with_dependencies('embeddings', 'public', 'rag');
    PERFORM move_table_with_dependencies('document_changes_log', 'public', 'rag');
    PERFORM move_table_with_dependencies('statistics', 'public', 'rag');
END $$;

-- Mover tabelas de regras (apenas as que existem)
DO $$ 
BEGIN
    PERFORM move_table_with_dependencies('rules', 'public', 'rules');
    PERFORM move_table_with_dependencies('rule_interactions', 'public', 'rules');
    PERFORM move_table_with_dependencies('rule_metrics', 'public', 'rules');
END $$;

-- Verificar resultado após movimentação
DO $$ 
BEGIN
    RAISE NOTICE 'Tabelas após a movimentação:';
END $$;

SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('public', 'rag', 'rules')
ORDER BY schemaname, tablename;

-- Habilitar RLS apenas nas tabelas que foram movidas com sucesso
DO $$ 
DECLARE
    v_table record;
BEGIN
    FOR v_table IN (
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname IN ('rag', 'rules')
    ) LOOP
        EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', 
            v_table.schemaname, v_table.tablename);
        RAISE NOTICE 'RLS habilitado para %.%', 
            v_table.schemaname, v_table.tablename;
    END LOOP;
END $$;

-- Atualizar search_path nas funções (apenas se existirem)
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'generate_embedding') THEN
        ALTER FUNCTION generate_embedding(text) SET search_path = rag, public;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'match_documents') THEN
        ALTER FUNCTION match_documents(vector, float, integer) SET search_path = rag, public;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cleanup_old_documents') THEN
        ALTER FUNCTION cleanup_old_documents(integer) SET search_path = rag, public;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'cleanup_orphaned_embeddings') THEN
        ALTER FUNCTION cleanup_orphaned_embeddings() SET search_path = rag, public;
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_system_metrics') THEN
        ALTER FUNCTION get_system_metrics() SET search_path = rag, public;
    END IF;
END $$; 