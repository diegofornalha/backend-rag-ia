-- Funções para o sistema RAG

-- Habilita a extensão vector se não estiver habilitada
CREATE EXTENSION IF NOT EXISTS vector;

-- Habilita a extensão pg_trgm se não estiver habilitada
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Cria tabela base de conhecimento se não existir
CREATE TABLE IF NOT EXISTS rag.base_conhecimento (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    tipo TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ativo',
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cria tabela de embeddings se não existir
CREATE TABLE IF NOT EXISTS rag.embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES rag.base_conhecimento(id) ON DELETE CASCADE,
    embedding vector(384) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Função para buscar documentos por similaridade
CREATE OR REPLACE FUNCTION rag.match_documents(
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id UUID,
    titulo TEXT,
    conteudo TEXT,
    similarity float
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        d.id,
        d.titulo,
        d.conteudo,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM rag.base_conhecimento d
    JOIN rag.embeddings e ON d.id = e.documento_id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
$$; 