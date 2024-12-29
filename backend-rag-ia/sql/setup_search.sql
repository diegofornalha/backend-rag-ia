-- Habilita a extensão vector se ainda não estiver habilitada
CREATE EXTENSION IF NOT EXISTS vector;

-- Função para buscar documentos similares
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.5,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM
        documents d
        INNER JOIN embeddings e ON d.id = e.document_id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 