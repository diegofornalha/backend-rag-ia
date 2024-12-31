-- Verificar tabelas existentes antes de mover
DO $$ 
BEGIN
    RAISE NOTICE 'Iniciando migração inicial...';
END $$;

-- Criar os schemas necessários
CREATE SCHEMA IF NOT EXISTS rag;
CREATE SCHEMA IF NOT EXISTS rules;
CREATE SCHEMA IF NOT EXISTS auth;

-- Função auxiliar para mover tabelas com segurança
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

-- Mover tabelas existentes para os schemas corretos
DO $$ 
BEGIN
    -- Mover tabelas principais
    PERFORM move_table_with_dependencies('01_base_conhecimento_regras_geral', 'public', 'rag');
    PERFORM move_table_with_dependencies('02_embeddings_regras_geral', 'public', 'rag');
    PERFORM move_table_with_dependencies('statistics', 'public', 'rag');
    PERFORM move_table_with_dependencies('rule_counts', 'public', 'rules');
    
    -- Remover tabela antiga se existir
    DROP TABLE IF EXISTS rag.knowledge_base CASCADE;
END $$;

-- Verificar resultado da migração
DO $$ 
BEGIN
    RAISE NOTICE 'Verificando resultado da migração...';
END $$;

SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('public', 'rag', 'rules')
ORDER BY schemaname, tablename;

-- Atualizar search_path para as funções
DO $$ 
BEGIN
    -- Funções de busca
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'match_documents') THEN
        ALTER FUNCTION match_documents(vector, float, integer) SET search_path = rag, public;
    END IF;

    -- Funções de verificação
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'check_duplicate_content') THEN
        ALTER FUNCTION check_duplicate_content(text, uuid) SET search_path = rag, public;
    END IF;

    -- Funções de atualização
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        ALTER FUNCTION update_updated_at_column() SET search_path = rag, public;
    END IF;
END $$;

-- Verificar e atualizar permissões
DO $$
BEGIN
    -- Garantir que authenticated tem acesso aos schemas
    GRANT USAGE ON SCHEMA rag TO authenticated;
    GRANT USAGE ON SCHEMA rules TO authenticated;
    GRANT USAGE ON SCHEMA auth TO authenticated;
END $$; 