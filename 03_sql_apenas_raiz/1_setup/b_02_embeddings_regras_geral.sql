-- Cria a tabela de embeddings
DROP TABLE IF EXISTS rag."02_embeddings_regras_geral" CASCADE;

-- Cria a tabela
CREATE TABLE rag."02_embeddings_regras_geral" (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id uuid NOT NULL REFERENCES rag."01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(1536),
    processing_status text NOT NULL DEFAULT 'pending',
    content_hash text NOT NULL,
    last_embedding_update timestamp with time zone,
    embedding_attempts integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Habilita RLS
ALTER TABLE rag."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Cria índices
CREATE INDEX IF NOT EXISTS idx_02_embeddings_regras_geral_document_id 
ON rag."02_embeddings_regras_geral" (document_id);

CREATE INDEX IF NOT EXISTS idx_02_embeddings_regras_geral_content_hash
ON rag."02_embeddings_regras_geral" (content_hash);

-- Cria trigger para updated_at
CREATE TRIGGER update_02_embeddings_regras_geral_updated_at
    BEFORE UPDATE
    ON rag."02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.update_updated_at_column(); 