-- Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Verificar e aplicar políticas de forma segura
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
        -- Habilitar RLS para as tabelas
        ALTER TABLE IF EXISTS rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;
        ALTER TABLE IF EXISTS rag."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

        -- Remover políticas existentes (caso existam)
        DROP POLICY IF EXISTS "Permitir select para authenticated" ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS "Permitir insert para authenticated e service_role" ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS "Permitir update para service_role" ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS "Permitir delete para service_role" ON rag."01_base_conhecimento_regras_geral";

        DROP POLICY IF EXISTS "Permitir select para authenticated" ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS "Permitir insert para service_role" ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS "Permitir update para service_role" ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS "Permitir delete para service_role" ON rag."02_embeddings_regras_geral";

        -- Políticas para 01_base_conhecimento_regras_geral
        CREATE POLICY "Permitir select para authenticated"
        ON rag."01_base_conhecimento_regras_geral"
        FOR SELECT
        USING (auth.role() = 'authenticated');

        CREATE POLICY "Permitir insert para authenticated e service_role"
        ON rag."01_base_conhecimento_regras_geral"
        FOR INSERT
        WITH CHECK (auth.role() IN ('authenticated', 'service_role'));

        CREATE POLICY "Permitir update para service_role"
        ON rag."01_base_conhecimento_regras_geral"
        FOR UPDATE
        USING (auth.role() = 'service_role')
        WITH CHECK (auth.role() = 'service_role');

        CREATE POLICY "Permitir delete para service_role"
        ON rag."01_base_conhecimento_regras_geral"
        FOR DELETE
        USING (auth.role() = 'service_role');

        -- Políticas para 02_embeddings_regras_geral
        CREATE POLICY "Permitir select para authenticated"
        ON rag."02_embeddings_regras_geral"
        FOR SELECT
        USING (auth.role() = 'authenticated');

        CREATE POLICY "Permitir insert para service_role"
        ON rag."02_embeddings_regras_geral"
        FOR INSERT
        WITH CHECK (auth.role() = 'service_role');

        CREATE POLICY "Permitir update para service_role"
        ON rag."02_embeddings_regras_geral"
        FOR UPDATE
        USING (auth.role() = 'service_role')
        WITH CHECK (auth.role() = 'service_role');

        CREATE POLICY "Permitir delete para service_role"
        ON rag."02_embeddings_regras_geral"
        FOR DELETE
        USING (auth.role() = 'service_role');

        RAISE NOTICE 'Políticas aplicadas com sucesso';
    ELSE
        RAISE NOTICE 'Tabelas ainda não existem. Execute primeiro o script de migração.';
    END IF;
END
$$;
