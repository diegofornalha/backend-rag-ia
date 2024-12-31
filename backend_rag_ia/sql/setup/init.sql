-- Habilitar a extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Remover função existente
DROP FUNCTION IF EXISTS match_documents(vector, double precision, integer);

-- Criar tabela de documentos
CREATE TABLE IF NOT EXISTS "01_base_conhecimento_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de embeddings
CREATE TABLE IF NOT EXISTS "02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES "01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para busca por similaridade
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx ON "02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Função para gerar embeddings
CREATE OR REPLACE FUNCTION generate_embedding(input_text text)
RETURNS vector
LANGUAGE plpgsql
AS $$
BEGIN
    -- Implementação será feita via API
    RETURN NULL;
END;
$$;

-- Função para buscar documentos similares
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector,
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    titulo TEXT,
    conteudo TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.titulo,
        d.conteudo,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM "01_base_conhecimento_regras_geral" d
    JOIN "02_embeddings_regras_geral" e ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$; 