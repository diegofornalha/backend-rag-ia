-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Criar schema se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Dropar tabela se existir (isso vai remover todos os dados!)
DROP TABLE IF EXISTS rag."01_base_conhecimento_regras_geral" CASCADE;

-- Criar tabela principal de documentos
CREATE TABLE rag."01_base_conhecimento_regras_geral" (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titulo TEXT NOT NULL,
    conteudo JSONB NOT NULL,
    metadata JSONB,
    document_hash TEXT UNIQUE,
    version_key TEXT,
    error_log TEXT,
    processing_status TEXT DEFAULT 'pending',
    last_embedding_update TIMESTAMP WITH TIME ZONE,
    embedding_attempts INTEGER DEFAULT 0,
    content_hash TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_document_hash 
ON rag."01_base_conhecimento_regras_geral"(document_hash);

CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_content_hash
ON rag."01_base_conhecimento_regras_geral"(content_hash);

CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_version_key
ON rag."01_base_conhecimento_regras_geral"(version_key);

-- Criar índice GIN para busca em JSONB
CREATE INDEX IF NOT EXISTS idx_01_base_conhecimento_conteudo_gin 
ON rag."01_base_conhecimento_regras_geral" USING GIN (conteudo);

-- Habilitar RLS
ALTER TABLE rag."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION rag.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- Criar trigger para atualizar timestamp
DROP TRIGGER IF EXISTS update_01_base_conhecimento_updated_at 
ON rag."01_base_conhecimento_regras_geral";

CREATE TRIGGER update_01_base_conhecimento_updated_at
    BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.update_updated_at_column(); 