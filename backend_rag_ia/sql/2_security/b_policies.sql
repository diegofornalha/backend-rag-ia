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
        -- Remover políticas existentes para documentos
        DROP POLICY IF EXISTS select_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS insert_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS update_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS delete_documentos ON rag."01_base_conhecimento_regras_geral";

        -- Remover políticas existentes para embeddings
        DROP POLICY IF EXISTS select_embeddings ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS insert_embeddings ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS update_embeddings ON rag."02_embeddings_regras_geral";
        DROP POLICY IF EXISTS delete_embeddings ON rag."02_embeddings_regras_geral";

        -- Habilitar RLS para tabelas do RAG
        ALTER TABLE IF EXISTS rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;
        ALTER TABLE IF EXISTS rag."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;
        ALTER TABLE IF EXISTS rag.statistics ENABLE ROW LEVEL SECURITY;

        -- Políticas para documentos
        CREATE POLICY select_documentos ON rag."01_base_conhecimento_regras_geral"
            FOR SELECT
            USING (
                (metadata->>'public')::boolean = true
                OR
                auth.uid() = owner_id
            );

        CREATE POLICY insert_documentos ON rag."01_base_conhecimento_regras_geral"
            FOR INSERT
            WITH CHECK (
                auth.uid() = owner_id
            );

        CREATE POLICY update_documentos ON rag."01_base_conhecimento_regras_geral"
            FOR UPDATE
            USING (
                auth.uid() = owner_id
            );

        CREATE POLICY delete_documentos ON rag."01_base_conhecimento_regras_geral"
            FOR DELETE
            USING (
                auth.uid() = owner_id
            );

        -- Políticas para embeddings
        CREATE POLICY select_embeddings ON rag."02_embeddings_regras_geral"
            FOR SELECT
            USING (
                EXISTS (
                    SELECT 1
                    FROM rag."01_base_conhecimento_regras_geral" d
                    WHERE d.id = documento_id
                    AND (
                        (d.metadata->>'public')::boolean = true
                        OR
                        auth.uid() = d.owner_id
                    )
                )
            );

        CREATE POLICY insert_embeddings ON rag."02_embeddings_regras_geral"
            FOR INSERT
            WITH CHECK (
                EXISTS (
                    SELECT 1
                    FROM rag."01_base_conhecimento_regras_geral" d
                    WHERE d.id = documento_id
                    AND auth.uid() = d.owner_id
                )
            );

        CREATE POLICY update_embeddings ON rag."02_embeddings_regras_geral"
            FOR UPDATE
            USING (
                EXISTS (
                    SELECT 1
                    FROM rag."01_base_conhecimento_regras_geral" d
                    WHERE d.id = documento_id
                    AND auth.uid() = d.owner_id
                )
            );

        CREATE POLICY delete_embeddings ON rag."02_embeddings_regras_geral"
            FOR DELETE
            USING (
                EXISTS (
                    SELECT 1
                    FROM rag."01_base_conhecimento_regras_geral" d
                    WHERE d.id = documento_id
                    AND auth.uid() = d.owner_id
                )
            );

        -- Políticas para statistics
        CREATE POLICY select_statistics ON rag.statistics
            FOR SELECT
            USING (true);  -- Leitura pública

        CREATE POLICY insert_statistics ON rag.statistics
            FOR INSERT
            WITH CHECK (auth.uid() IS NOT NULL);  -- Apenas usuários autenticados

        RAISE NOTICE 'Políticas aplicadas com sucesso para as tabelas do schema rag';
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
        -- Habilitar RLS para tabelas de rules
        ALTER TABLE IF EXISTS rules.rule_counts ENABLE ROW LEVEL SECURITY;

        -- Políticas para rule_counts
        CREATE POLICY select_rule_counts ON rules.rule_counts
            FOR SELECT
            USING (true);  -- Leitura pública

        CREATE POLICY insert_rule_counts ON rules.rule_counts
            FOR INSERT
            WITH CHECK (auth.uid() IS NOT NULL);  -- Apenas usuários autenticados

        RAISE NOTICE 'Políticas aplicadas com sucesso para as tabelas do schema rules';
    ELSE
        RAISE NOTICE 'Tabelas do schema rules ainda não existem. Execute primeiro o script de migração.';
    END IF;
END
$$;
