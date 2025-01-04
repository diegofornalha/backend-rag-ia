-- 1. Criar schema e configurar permissões básicas
CREATE SCHEMA IF NOT EXISTS rag;

-- Garantir permissões básicas
GRANT USAGE ON SCHEMA rag TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA rag TO postgres, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON TABLES TO postgres, anon, authenticated, service_role;

-- 2. Criar a tabela no schema rag
CREATE TABLE IF NOT EXISTS rag."01_base_conhecimento_regras_geral" (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    version_key text,
    titulo text,
    conteudo text,
    error_log text,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Configurar RLS
-- Habilitar RLS na tabela
ALTER TABLE rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Remover políticas existentes se houver
DROP POLICY IF EXISTS anon_select_documentos ON rag."01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS insert_documentos ON rag."01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS update_documentos ON rag."01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS delete_documentos ON rag."01_base_conhecimento_regras_geral";

-- Criar novas políticas
-- Política para leitura (anônimo e autenticado)
CREATE POLICY anon_select_documentos ON rag."01_base_conhecimento_regras_geral"
    FOR SELECT
    TO authenticated, anon
    USING (true);

-- Política para inserção (apenas usuários autenticados)
CREATE POLICY insert_documentos ON rag."01_base_conhecimento_regras_geral"
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Política para atualização (apenas usuários autenticados)
CREATE POLICY update_documentos ON rag."01_base_conhecimento_regras_geral"
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Política para deleção (apenas usuários autenticados)
CREATE POLICY delete_documentos ON rag."01_base_conhecimento_regras_geral"
    FOR DELETE
    TO authenticated
    USING (true); 