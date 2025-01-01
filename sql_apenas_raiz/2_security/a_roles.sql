-- Roles para acesso às tabelas de conhecimento
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'conhecimento_reader') THEN
        CREATE ROLE conhecimento_reader;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'conhecimento_writer') THEN
        CREATE ROLE conhecimento_writer;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'conhecimento_admin') THEN
        CREATE ROLE conhecimento_admin;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'authenticated') THEN
        CREATE ROLE authenticated;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'service_role') THEN
        CREATE ROLE service_role;
    END IF;
END
$$;

-- Permissões nos schemas
DO $$
BEGIN
    -- Criar schemas se não existirem
    CREATE SCHEMA IF NOT EXISTS rag;
    CREATE SCHEMA IF NOT EXISTS rules;
    
    -- Dar permissões nos schemas
    GRANT USAGE ON SCHEMA rag TO conhecimento_reader, conhecimento_writer, conhecimento_admin;
    GRANT USAGE ON SCHEMA rules TO conhecimento_reader, conhecimento_writer, conhecimento_admin;
END
$$;

-- Permissões nas tabelas (apenas se existirem)
DO $$
DECLARE
    table_exists boolean;
BEGIN
    -- Verificar tabelas do schema rag
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'rag' 
        AND table_name = '01_base_conhecimento_regras_geral'
    ) INTO table_exists;
    
    IF table_exists THEN
        -- Permissões para conhecimento_reader
        GRANT SELECT ON rag."01_base_conhecimento_regras_geral" TO conhecimento_reader;
        GRANT SELECT ON rag."02_embeddings_regras_geral" TO conhecimento_reader;
        GRANT SELECT ON rag.statistics TO conhecimento_reader;
        
        -- Permissões para conhecimento_writer
        GRANT SELECT, INSERT, UPDATE ON rag."01_base_conhecimento_regras_geral" TO conhecimento_writer;
        GRANT SELECT, INSERT, UPDATE ON rag."02_embeddings_regras_geral" TO conhecimento_writer;
        GRANT SELECT, INSERT, UPDATE ON rag.statistics TO conhecimento_writer;
        
        -- Permissões para conhecimento_admin
        GRANT ALL ON ALL TABLES IN SCHEMA rag TO conhecimento_admin;
    ELSE
        RAISE NOTICE 'Tabelas do schema rag ainda não existem. Execute primeiro o script de migração.';
    END IF;
    
    -- Verificar tabelas do schema rules
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'rules' 
        AND table_name = 'rule_counts'
    ) INTO table_exists;
    
    IF table_exists THEN
        GRANT SELECT ON rules.rule_counts TO conhecimento_reader;
        GRANT SELECT, INSERT, UPDATE ON rules.rule_counts TO conhecimento_writer;
        GRANT ALL ON ALL TABLES IN SCHEMA rules TO conhecimento_admin;
    ELSE
        RAISE NOTICE 'Tabelas do schema rules ainda não existem. Execute primeiro o script de migração.';
    END IF;
END
$$;

-- Permissões em funções (apenas se existirem)
DO $$
DECLARE
    func_exists boolean;
BEGIN
    -- Verificar função match_documents
    SELECT EXISTS (
        SELECT FROM pg_proc WHERE proname = 'match_documents'
    ) INTO func_exists;
    
    IF func_exists THEN
        GRANT EXECUTE ON FUNCTION match_documents(vector, float, integer) TO conhecimento_reader, conhecimento_writer;
    END IF;
    
    -- Verificar função check_duplicate_content
    SELECT EXISTS (
        SELECT FROM pg_proc WHERE proname = 'check_duplicate_content'
    ) INTO func_exists;
    
    IF func_exists THEN
        GRANT EXECUTE ON FUNCTION check_duplicate_content(text, uuid) TO conhecimento_reader, conhecimento_writer;
    END IF;
    
    -- Verificar função update_updated_at_column
    SELECT EXISTS (
        SELECT FROM pg_proc WHERE proname = 'update_updated_at_column'
    ) INTO func_exists;
    
    IF func_exists THEN
        GRANT EXECUTE ON FUNCTION update_updated_at_column() TO conhecimento_writer;
    END IF;
    
    -- Permissões gerais em funções para admin
    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA rag TO conhecimento_admin;
    GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA rules TO conhecimento_admin;
END
$$;

-- Permissões para authenticated
GRANT conhecimento_writer TO authenticated;

-- Permissões para service_role
GRANT conhecimento_admin TO service_role; 