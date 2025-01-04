-- Ajustar permissões do schema rag
DO $$
BEGIN
    -- Garantir que o schema existe
    CREATE SCHEMA IF NOT EXISTS rag;

    -- Garantir que o usuário anon tem acesso ao schema
    GRANT USAGE ON SCHEMA rag TO anon;
    GRANT USAGE ON SCHEMA rag TO authenticated;
    GRANT USAGE ON SCHEMA rag TO service_role;

    -- Garantir acesso às tabelas existentes
    GRANT ALL ON ALL TABLES IN SCHEMA rag TO anon;
    GRANT ALL ON ALL TABLES IN SCHEMA rag TO authenticated;
    GRANT ALL ON ALL TABLES IN SCHEMA rag TO service_role;

    -- Garantir acesso às sequências
    GRANT ALL ON ALL SEQUENCES IN SCHEMA rag TO anon;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA rag TO authenticated;
    GRANT ALL ON ALL SEQUENCES IN SCHEMA rag TO service_role;

    -- Garantir acesso às funções
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA rag TO anon;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA rag TO authenticated;
    GRANT ALL ON ALL FUNCTIONS IN SCHEMA rag TO service_role;

    -- Alterar o search_path padrão para incluir o schema rag
    ALTER DATABASE postgres SET search_path TO rag, public;

    -- Atualizar as políticas de RLS
    ALTER TABLE IF EXISTS rag."01_base_conhecimento_regras_geral" FORCE ROW LEVEL SECURITY;
    ALTER TABLE IF EXISTS rag."02_embeddings_regras_geral" FORCE ROW LEVEL SECURITY;

    -- Criar políticas de acesso para anon
    DROP POLICY IF EXISTS anon_select_documentos ON rag."01_base_conhecimento_regras_geral";
    CREATE POLICY anon_select_documentos ON rag."01_base_conhecimento_regras_geral"
        FOR SELECT
        TO anon
        USING (true);

    DROP POLICY IF EXISTS anon_select_embeddings ON rag."02_embeddings_regras_geral";
    CREATE POLICY anon_select_embeddings ON rag."02_embeddings_regras_geral"
        FOR SELECT
        TO anon
        USING (true);

    RAISE NOTICE 'Permissões do schema rag atualizadas com sucesso';
END
$$; 