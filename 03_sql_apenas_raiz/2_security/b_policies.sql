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
        -- Remover políticas existentes
        DROP POLICY IF EXISTS select_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS insert_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS update_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS delete_documentos ON rag."01_base_conhecimento_regras_geral";
        DROP POLICY IF EXISTS anon_select_documentos ON rag."01_base_conhecimento_regras_geral";

        -- Habilitar RLS
        ALTER TABLE IF EXISTS rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

        -- Política para leitura (anônimo e autenticado)
        CREATE POLICY anon_select_documentos ON rag."01_base_conhecimento_regras_geral"
            FOR SELECT
            TO authenticated
            USING (true);

        -- Política para inserção (apenas usuários permanentes)
        CREATE POLICY insert_documentos ON rag."01_base_conhecimento_regras_geral"
            AS RESTRICTIVE
            FOR INSERT
            TO authenticated
            WITH CHECK ((auth.jwt() ->> 'is_anonymous')::boolean IS FALSE);

        -- Política para atualização (apenas usuários permanentes)
        CREATE POLICY update_documentos ON rag."01_base_conhecimento_regras_geral"
            AS RESTRICTIVE
            FOR UPDATE
            TO authenticated
            USING ((auth.jwt() ->> 'is_anonymous')::boolean IS FALSE)
            WITH CHECK ((auth.jwt() ->> 'is_anonymous')::boolean IS FALSE);

        -- Política para deleção (apenas usuários permanentes)
        CREATE POLICY delete_documentos ON rag."01_base_conhecimento_regras_geral"
            AS RESTRICTIVE
            FOR DELETE
            TO authenticated
            USING ((auth.jwt() ->> 'is_anonymous')::boolean IS FALSE);

        RAISE NOTICE 'Políticas aplicadas com sucesso';
    ELSE
        RAISE NOTICE 'Tabelas ainda não existem. Execute primeiro o script de migração.';
    END IF;
END
$$;
