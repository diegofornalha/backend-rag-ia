-- Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Criar extensão se não existir
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar tabela
CREATE TABLE IF NOT EXISTS rag."01_base_conhecimento_regras_geral" (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    titulo text NOT NULL,
    conteudo jsonb NOT NULL,
    metadata jsonb,
    document_hash text,
    version_key text,
    error_log text,
    processing_status text DEFAULT 'pending',
    last_embedding_update timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    embedding_attempts integer DEFAULT 0,
    content_hash text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_regras_geral_version_key 
ON rag."01_base_conhecimento_regras_geral"(version_key);

CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_regras_geral_document_hash 
ON rag."01_base_conhecimento_regras_geral"(document_hash);

CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_regras_geral_content_hash 
ON rag."01_base_conhecimento_regras_geral"(content_hash);

-- Criar trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_01_base_conhecimento_regras_geral_updated_at 
ON rag."01_base_conhecimento_regras_geral";

CREATE TRIGGER update_01_base_conhecimento_regras_geral_updated_at
    BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Configurar permissões
ALTER TABLE rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso
DROP POLICY IF EXISTS "Permitir select para authenticated" ON rag."01_base_conhecimento_regras_geral";
CREATE POLICY "Permitir select para authenticated"
ON rag."01_base_conhecimento_regras_geral"
FOR SELECT
USING (auth.role() = 'authenticated');

DROP POLICY IF EXISTS "Permitir insert para authenticated e service_role" ON rag."01_base_conhecimento_regras_geral";
CREATE POLICY "Permitir insert para authenticated e service_role"
ON rag."01_base_conhecimento_regras_geral"
FOR INSERT
WITH CHECK (auth.role() IN ('authenticated', 'service_role'));

DROP POLICY IF EXISTS "Permitir update para service_role" ON rag."01_base_conhecimento_regras_geral";
CREATE POLICY "Permitir update para service_role"
ON rag."01_base_conhecimento_regras_geral"
FOR UPDATE
USING (auth.role() = 'service_role')
WITH CHECK (auth.role() = 'service_role');

DROP POLICY IF EXISTS "Permitir delete para service_role" ON rag."01_base_conhecimento_regras_geral";
CREATE POLICY "Permitir delete para service_role"
ON rag."01_base_conhecimento_regras_geral"
FOR DELETE
USING (auth.role() = 'service_role');

-- Conceder permissões ao schema e tabela
GRANT USAGE ON SCHEMA rag TO postgres, anon, authenticated, service_role;
GRANT ALL ON TABLE rag."01_base_conhecimento_regras_geral" TO postgres, service_role;
GRANT SELECT, INSERT ON TABLE rag."01_base_conhecimento_regras_geral" TO authenticated;
GRANT SELECT ON TABLE rag."01_base_conhecimento_regras_geral" TO anon; 