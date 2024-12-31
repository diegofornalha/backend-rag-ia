-- Dropar tabela se existir
DROP TABLE IF EXISTS public."02_embeddings_regras_geral" CASCADE;

-- Criar tabela de embeddings
CREATE TABLE public."02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES public."01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(384),
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Criar índice para documento_id
CREATE INDEX idx_embedding_documento_id 
ON public."02_embeddings_regras_geral"(documento_id);

-- Criar índice para busca por similaridade
CREATE INDEX idx_embedding_vector 
ON public."02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Habilitar RLS
ALTER TABLE public."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Criar trigger para atualizar timestamp
DROP TRIGGER IF EXISTS update_embeddings_updated_at 
ON public."02_embeddings_regras_geral";

CREATE TRIGGER update_embeddings_updated_at
    BEFORE UPDATE ON public."02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at_column();

-- Dropar função existente
DROP FUNCTION IF EXISTS public.match_documents(vector(384), float, int);

-- Criar função para busca semântica
CREATE OR REPLACE FUNCTION public.match_documents(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.8,
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
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        d.conteudo as content,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM public."02_embeddings_regras_geral" e
    JOIN public."01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 