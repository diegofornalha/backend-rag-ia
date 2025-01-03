-- Habilita a extensão vector se ainda não estiver habilitada
CREATE EXTENSION IF NOT EXISTS vector;

-- Remover função existente
DROP FUNCTION IF EXISTS match_documents(vector, double precision, integer);

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
SECURITY DEFINER
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