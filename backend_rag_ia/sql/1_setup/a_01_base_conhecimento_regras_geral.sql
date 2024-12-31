-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Dropar tabela se existir (isso vai remover todos os dados!)
DROP TABLE IF EXISTS public."01_base_conhecimento_regras_geral" CASCADE;

-- Criar tabela principal de documentos
CREATE TABLE public."01_base_conhecimento_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    conteudo JSONB NOT NULL,
    content_hash TEXT GENERATED ALWAYS AS (encode(sha256((conteudo->>'text')::bytea), 'hex')) STORED,
    metadata JSONB DEFAULT '{}'::jsonb,
    owner_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_content UNIQUE (content_hash, owner_id)
);

-- Criar índices
CREATE INDEX idx_content_hash 
ON public."01_base_conhecimento_regras_geral"(content_hash);

-- Criar índice GIN para busca em JSONB
CREATE INDEX idx_conteudo_gin 
ON public."01_base_conhecimento_regras_geral" USING GIN (conteudo);

-- Habilitar RLS
ALTER TABLE public."01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger para atualizar timestamp
DROP TRIGGER IF EXISTS update_base_conhecimento_updated_at 
ON public."01_base_conhecimento_regras_geral";

CREATE TRIGGER update_base_conhecimento_updated_at
    BEFORE UPDATE ON public."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column(); 