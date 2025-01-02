-- Define o schema padrão
SET search_path TO rag;

-- Cria schema rag se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Habilita a extensão vector no schema rag
CREATE EXTENSION IF NOT EXISTS vector SCHEMA rag;

-- Remove funções existentes
DROP FUNCTION IF EXISTS rag.generate_embedding(text);
DROP FUNCTION IF EXISTS rag.match_documents(vector, float, int);
DROP FUNCTION IF EXISTS rag.match_documents(vector(384), float, int);
DROP FUNCTION IF EXISTS rag.buscar_documentos(text, int);

-- Função para buscar documentos
CREATE OR REPLACE FUNCTION rag.buscar_documentos(
    termo_busca text,
    limite int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    titulo text,
    conteudo jsonb,
    version_key text,
    error_log jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.titulo,
        d.conteudo,
        d.version_key,
        d.error_log
    FROM "01_base_conhecimento_regras_geral" d
    WHERE 
        d.titulo ILIKE '%' || termo_busca || '%'
        OR d.conteudo::text ILIKE '%' || termo_busca || '%'
    LIMIT limite;
END;
$$;

-- Função para buscar embeddings
CREATE OR REPLACE FUNCTION rag.buscar_embeddings(
    termo_busca text,
    limite int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    processing_status text,
    content_hash text,
    last_embedding_update timestamptz,
    embedding_attempts int4
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        e.processing_status,
        e.content_hash,
        e.last_embedding_update,
        e.embedding_attempts
    FROM "02_embeddings_regras_geral" e
    JOIN "01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 
        d.titulo ILIKE '%' || termo_busca || '%'
        OR d.conteudo::text ILIKE '%' || termo_busca || '%'
    LIMIT limite;
END;
$$;

-- Função para busca semântica
CREATE OR REPLACE FUNCTION rag.match_documents_v2(
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    content text,
    similarity float,
    processing_status text,
    embedding_attempts int4
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        d.conteudo->>'text' as content,
        1 - (e.embedding <=> query_embedding) as similarity,
        e.processing_status,
        e.embedding_attempts
    FROM "02_embeddings_regras_geral" e
    JOIN "01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 