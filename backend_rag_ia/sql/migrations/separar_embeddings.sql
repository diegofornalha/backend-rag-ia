-- Criar nova tabela para embeddings
CREATE TABLE IF NOT EXISTS "02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL REFERENCES "01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(384),  -- Dimensão do modelo all-MiniLM-L6-v2
    modelo TEXT NOT NULL DEFAULT 'all-MiniLM-L6-v2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT fk_documento 
        FOREIGN KEY(documento_id) 
        REFERENCES "01_base_conhecimento_regras_geral"(id)
        ON DELETE CASCADE
);

-- Primeiro verificar se a tabela antiga ainda existe e migrar dados
DO $$ 
BEGIN
    IF EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public' 
        AND tablename = 'base_conhecimento_regras_geral'
    ) THEN
        -- Migrar dados da tabela antiga
        INSERT INTO "02_embeddings_regras_geral" (documento_id, embedding, created_at, updated_at)
        SELECT 
            id as documento_id,
            embedding,
            created_at,
            updated_at
        FROM base_conhecimento_regras_geral
        WHERE embedding IS NOT NULL;

        -- Remover coluna embedding da tabela antiga
        ALTER TABLE base_conhecimento_regras_geral
        DROP COLUMN IF EXISTS embedding;

        -- Renomear tabela antiga para novo padrão
        ALTER TABLE base_conhecimento_regras_geral 
        RENAME TO "01_base_conhecimento_regras_geral";
    END IF;
END $$;

-- Criar índice para buscas vetoriais
CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
ON "02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Criar função para manter updated_at atualizado
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger em ambas as tabelas
DROP TRIGGER IF EXISTS update_embeddings_regras_updated_at ON "02_embeddings_regras_geral";
CREATE TRIGGER update_embeddings_regras_updated_at
    BEFORE UPDATE ON "02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Criar políticas RLS para embeddings
ALTER TABLE "02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

CREATE POLICY select_embeddings ON "02_embeddings_regras_geral"
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = "02_embeddings_regras_geral".documento_id
            AND (
                (d.metadata->>'public')::boolean = true
                OR
                auth.uid() = d.owner_id
            )
        )
    );

CREATE POLICY insert_embeddings ON "02_embeddings_regras_geral"
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = "02_embeddings_regras_geral".documento_id
            AND auth.uid() = d.owner_id
        )
    );

CREATE POLICY update_embeddings ON "02_embeddings_regras_geral"
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = "02_embeddings_regras_geral".documento_id
            AND auth.uid() = d.owner_id
        )
    );

CREATE POLICY delete_embeddings ON "02_embeddings_regras_geral"
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = "02_embeddings_regras_geral".documento_id
            AND auth.uid() = d.owner_id
        )
    );

-- Criar função para busca semântica
CREATE OR REPLACE FUNCTION match_documents_v2(
    query_embedding vector(384),
    match_threshold float,
    match_count int
)
RETURNS TABLE (
    id uuid,
    documento_id uuid,
    content text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.documento_id,
        d.conteudo as content,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM "02_embeddings_regras_geral" e
    JOIN "01_base_conhecimento_regras_geral" d ON e.documento_id = d.id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$; 