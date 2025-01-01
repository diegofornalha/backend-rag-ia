-- Define o schema padrão
SET search_path TO public;

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
    conteudo jsonb
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
        d.conteudo
    FROM "01_base_conhecimento_regras_geral" d
    WHERE 
        d.titulo ILIKE '%' || termo_busca || '%'
        OR d.conteudo::text ILIKE '%' || termo_busca || '%'
    LIMIT limite;
END;
$$;

-- Função para gerar embeddings
CREATE OR REPLACE FUNCTION rag.generate_embedding(text text)
RETURNS float[]
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag
AS $$
BEGIN
    -- Por enquanto retorna um array de 384 zeros
    -- Isso será substituído pela chamada real ao modelo
    RETURN array_fill(0::float, ARRAY[384]);
END;
$$;

-- Função para buscar documentos similares
CREATE OR REPLACE FUNCTION rag.match_documents(
    query_embedding float[],
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    content jsonb,
    similarity float
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
        d.conteudo as content,
        1 - (e.embedding <=> query_embedding::vector) as similarity
    FROM rag."02_embeddings_regras_geral" e
    JOIN rag."01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding::vector) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 