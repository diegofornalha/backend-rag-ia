-- Remover políticas existentes para documentos
DROP POLICY IF EXISTS select_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS insert_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS update_documentos ON "01_base_conhecimento_regras_geral";
DROP POLICY IF EXISTS delete_documentos ON "01_base_conhecimento_regras_geral";

-- Remover políticas existentes para embeddings
DROP POLICY IF EXISTS select_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS insert_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS update_embeddings ON "02_embeddings_regras_geral";
DROP POLICY IF EXISTS delete_embeddings ON "02_embeddings_regras_geral";

-- Adicionar coluna owner_id se não existir
ALTER TABLE "01_base_conhecimento_regras_geral" ADD COLUMN IF NOT EXISTS owner_id uuid;

-- Habilitar RLS para a tabela de documentos
ALTER TABLE IF EXISTS "01_base_conhecimento_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Habilitar RLS para a tabela de embeddings
ALTER TABLE IF EXISTS "02_embeddings_regras_geral" ENABLE ROW LEVEL SECURITY;

-- Política de select para documentos
CREATE POLICY select_documentos ON "01_base_conhecimento_regras_geral"
    FOR SELECT
    USING (
        (metadata->>'public')::boolean = true
        OR
        auth.uid() = owner_id
    );

-- Política de insert para documentos
CREATE POLICY insert_documentos ON "01_base_conhecimento_regras_geral"
    FOR INSERT
    WITH CHECK (
        auth.uid() = owner_id
    );

-- Política de update para documentos
CREATE POLICY update_documentos ON "01_base_conhecimento_regras_geral"
    FOR UPDATE
    USING (
        auth.uid() = owner_id
    );

-- Política de delete para documentos
CREATE POLICY delete_documentos ON "01_base_conhecimento_regras_geral"
    FOR DELETE
    USING (
        auth.uid() = owner_id
    );

-- Política de select para embeddings
CREATE POLICY select_embeddings ON "02_embeddings_regras_geral"
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND (
                (d.metadata->>'public')::boolean = true
                OR
                auth.uid() = d.owner_id
            )
        )
    );

-- Política de insert para embeddings
CREATE POLICY insert_embeddings ON "02_embeddings_regras_geral"
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    );

-- Política de update para embeddings
CREATE POLICY update_embeddings ON "02_embeddings_regras_geral"
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    );

-- Política de delete para embeddings
CREATE POLICY delete_embeddings ON "02_embeddings_regras_geral"
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1
            FROM "01_base_conhecimento_regras_geral" d
            WHERE d.id = documento_id
            AND auth.uid() = d.owner_id
        )
    ); 