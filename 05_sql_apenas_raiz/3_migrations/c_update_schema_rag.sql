-- Atualizar tabela base_conhecimento_regras_geral
ALTER TABLE rag."01_base_conhecimento_regras_geral"
ADD COLUMN IF NOT EXISTS version_key text,
ADD COLUMN IF NOT EXISTS error_log jsonb DEFAULT '{}'::jsonb;

-- Atualizar tabela embeddings_regras_geral
ALTER TABLE rag."02_embeddings_regras_geral"
ADD COLUMN IF NOT EXISTS processing_status text DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS content_hash text,
ADD COLUMN IF NOT EXISTS last_embedding_update timestamptz DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS embedding_attempts int4 DEFAULT 0;

-- Criar índices para as novas colunas
CREATE INDEX IF NOT EXISTS idx_version_key 
ON rag."01_base_conhecimento_regras_geral"(version_key);

CREATE INDEX IF NOT EXISTS idx_processing_status 
ON rag."02_embeddings_regras_geral"(processing_status);

CREATE INDEX IF NOT EXISTS idx_content_hash 
ON rag."02_embeddings_regras_geral"(content_hash);

-- Atualizar políticas RLS para as novas colunas
DO $$
BEGIN
    -- Atualizar política de select para considerar version_key
    DROP POLICY IF EXISTS select_documentos ON rag."01_base_conhecimento_regras_geral";
    CREATE POLICY select_documentos ON rag."01_base_conhecimento_regras_geral"
        FOR SELECT
        USING (
            (metadata->>'public')::boolean = true
            OR
            auth.uid() = owner_id
        );

    -- Atualizar política de select para embeddings
    DROP POLICY IF EXISTS select_embeddings ON rag."02_embeddings_regras_geral";
    CREATE POLICY select_embeddings ON rag."02_embeddings_regras_geral"
        FOR SELECT
        USING (
            EXISTS (
                SELECT 1 FROM rag."01_base_conhecimento_regras_geral" d
                WHERE d.id = rag."02_embeddings_regras_geral".documento_id
                AND (
                    (d.metadata->>'public')::boolean = true
                    OR
                    auth.uid() = d.owner_id
                )
            )
        );
END
$$; 