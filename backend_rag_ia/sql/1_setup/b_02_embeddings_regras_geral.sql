-- Criar tabela de embeddings
CREATE TABLE IF NOT EXISTS rag."02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES rag."01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(384),  -- Dimensão do modelo all-MiniLM-L6-v2
    modelo TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Criar índice para buscas vetoriais
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON rag."02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Criar índice para chave estrangeira
CREATE INDEX IF NOT EXISTS idx_documento_id 
ON rag."02_embeddings_regras_geral"(documento_id);

-- Habilitar RLS
ALTER TABLE rag."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Criar trigger para atualizar timestamp
DROP TRIGGER IF EXISTS update_embeddings_updated_at 
ON rag."02_embeddings_regras_geral";

CREATE TRIGGER update_embeddings_updated_at
    BEFORE UPDATE ON rag."02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.update_updated_at_column();

-- Criar função para busca semântica
CREATE OR REPLACE FUNCTION rag.match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.8,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    content text,
    similarity float
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        d.conteudo as content,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM rag."02_embeddings_regras_geral" e
    JOIN rag."01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 