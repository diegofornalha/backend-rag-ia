-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Criar tabela principal de documentos
CREATE TABLE IF NOT EXISTS rag."01_base_conhecimento_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    content_hash TEXT GENERATED ALWAYS AS (encode(sha256(conteudo::bytea), 'hex')) STORED,
    metadata JSONB DEFAULT '{}'::jsonb,
    owner_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_content UNIQUE (content_hash, owner_id)
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_content_hash 
ON rag."01_base_conhecimento_regras_geral"(content_hash);

-- Habilitar RLS
ALTER TABLE rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION rag.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger para atualizar timestamp
DROP TRIGGER IF EXISTS update_base_conhecimento_updated_at 
ON rag."01_base_conhecimento_regras_geral";

CREATE TRIGGER update_base_conhecimento_updated_at
    BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.update_updated_at_column(); 