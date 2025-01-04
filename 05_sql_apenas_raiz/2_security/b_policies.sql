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
        TO authenticated
        USING (
            status = 'ativo'
        );

        CREATE POLICY "Permitir insert para authenticated e service_role" 
        ON rag."01_base_conhecimento_regras_geral"
        FOR INSERT
        TO authenticated, service_role
        WITH CHECK (true);

        CREATE POLICY "Permitir update para service_role" 
        ON rag."01_base_conhecimento_regras_geral"
        FOR UPDATE
        TO service_role
        USING (true)
        WITH CHECK (true);

        CREATE POLICY "Permitir delete para service_role" 
        ON rag."01_base_conhecimento_regras_geral"
        FOR DELETE
        TO service_role
        USING (true);

        -- Políticas para 02_embeddings_regras_geral
        CREATE POLICY "Permitir select para authenticated" 
        ON rag."02_embeddings_regras_geral"
        FOR SELECT
        TO authenticated
        USING (
            EXISTS (
                SELECT 1
                FROM rag."01_base_conhecimento_regras_geral" d
                WHERE d.id = documento_id
                AND d.status = 'ativo'
            )
        );

        CREATE POLICY "Permitir insert para service_role" 
        ON rag."02_embeddings_regras_geral"
        FOR INSERT
        TO service_role
        WITH CHECK (true);

        CREATE POLICY "Permitir update para service_role" 
        ON rag."02_embeddings_regras_geral"
        FOR UPDATE
        TO service_role
        USING (true)
        WITH CHECK (true);

        CREATE POLICY "Permitir delete para service_role" 
        ON rag."02_embeddings_regras_geral"
        FOR DELETE
        TO service_role
        USING (true);

        RAISE NOTICE 'Políticas aplicadas com sucesso';
    ELSE
        RAISE NOTICE 'Tabelas ainda não existem. Execute primeiro o script de migração.';
    END IF;
END
$$;
