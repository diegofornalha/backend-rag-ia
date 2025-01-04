-- Criar schema rag se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Garantir permissões no schema
GRANT USAGE ON SCHEMA rag TO postgres, anon, authenticated, service_role;

-- Garantir permissões nas tabelas
GRANT ALL ON ALL TABLES IN SCHEMA rag TO postgres, anon, authenticated, service_role;

-- Garantir permissões em tabelas futuras
ALTER DEFAULT PRIVILEGES IN SCHEMA rag
GRANT ALL ON TABLES TO postgres, anon, authenticated, service_role;

-- Criar tabela 01_base_conhecimento_regras_geral se não existir
CREATE TABLE IF NOT EXISTS rag."01_base_conhecimento_regras_geral" (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo text,
    conteudo jsonb,
    error_log text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    processing_status text DEFAULT 'pending',
    content_hash text,
    last_embedding_update timestamp with time zone,
    embedding_attempts integer DEFAULT 0,
    metadata jsonb,
    document_hash text
);

-- Criar tabela 02_embeddings_regras_geral se não existir
CREATE TABLE IF NOT EXISTS rag."02_embeddings_regras_geral" (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id uuid REFERENCES rag."01_base_conhecimento_regras_geral"(id),
    embedding vector(1536),
    content_hash text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    processing_status text DEFAULT 'pending',
    last_embedding_update timestamp with time zone,
    embedding_attempts integer DEFAULT 0
);

-- Criar índice para otimizar buscas
CREATE INDEX IF NOT EXISTS idx_document_id ON rag."02_embeddings_regras_geral" (document_id);
CREATE INDEX IF NOT EXISTS idx_content_hash ON rag."02_embeddings_regras_geral" (content_hash);