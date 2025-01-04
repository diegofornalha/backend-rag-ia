-- Adiciona suporte a embeddings

-- Cria tabela de embeddings
CREATE TABLE IF NOT EXISTS rag."02_embeddings_regras_geral" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    documento_id UUID NOT NULL,
    embedding vector(384) NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_documento
        FOREIGN KEY (documento_id)
        REFERENCES rag."01_base_conhecimento_regras_geral"(id)
        ON DELETE CASCADE
);

-- Cria índice para busca por similaridade
CREATE INDEX IF NOT EXISTS idx_embeddings_embedding 
ON rag."02_embeddings_regras_geral" 
USING ivfflat (embedding vector_cosine_ops);

-- Função para gerar embeddings de teste
CREATE OR REPLACE FUNCTION rag.generate_test_embedding()
RETURNS vector
LANGUAGE plpgsql
AS $$
BEGIN
    -- Retorna um vetor de teste com 384 dimensões
    RETURN array_fill(0.1::float, ARRAY[384])::vector;
END;
$$;

-- Gera embeddings de teste para documentos existentes
INSERT INTO rag."02_embeddings_regras_geral" (documento_id, embedding)
SELECT 
    id,
    rag.generate_test_embedding()
FROM rag."01_base_conhecimento_regras_geral"
WHERE id NOT IN (
    SELECT documento_id 
    FROM rag."02_embeddings_regras_geral"
);

-- Adiciona trigger para atualizar timestamp
ALTER TABLE rag."01_base_conhecimento_regras_geral"
ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Cria função para atualizar timestamp
CREATE OR REPLACE FUNCTION rag.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Adiciona trigger para atualizar timestamp
ALTER TABLE rag."01_base_conhecimento_regras_geral"
DROP TRIGGER IF EXISTS update_timestamp_trigger ON rag."01_base_conhecimento_regras_geral";

CREATE TRIGGER update_timestamp_trigger
    BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.update_timestamp();

-- Configura RLS
ALTER TABLE rag."02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Políticas de acesso
CREATE POLICY select_embeddings ON rag."02_embeddings_regras_geral"
    FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1
            FROM rag."01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND d.status = 'ativo'
        )
    );

CREATE POLICY insert_embeddings ON rag."02_embeddings_regras_geral"
    FOR INSERT
    TO service_role
    WITH CHECK (true);

CREATE POLICY update_embeddings ON rag."02_embeddings_regras_geral"
    FOR UPDATE
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY delete_embeddings ON rag."02_embeddings_regras_geral"
    FOR DELETE
    TO service_role
    USING (true); 