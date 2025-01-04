-- Corrigido o nome da coluna 'exists' para 'is_exists' para evitar conflito com palavra reservada

-- Criar schema RAG se não existir
CREATE SCHEMA IF NOT EXISTS rag;

-- Criar a tabela principal no schema RAG
CREATE TABLE IF NOT EXISTS rag."01_base_conhecimento_regras_geral" (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    version_key text,
    titulo text,
    conteudo jsonb,
    error_log text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    processing_status text,
    content_hash text,
    last_embedding_update timestamptz,
    embedding_attempts int4 DEFAULT 0,
    metadata jsonb,
    document_hash text
);

-- Criar índices para melhorar performance
CREATE INDEX IF NOT EXISTS idx_base_conhecimento_version_key 
ON rag."01_base_conhecimento_regras_geral" (version_key);

CREATE INDEX IF NOT EXISTS idx_base_conhecimento_content_hash 
ON rag."01_base_conhecimento_regras_geral" (content_hash);

CREATE INDEX IF NOT EXISTS idx_base_conhecimento_document_hash 
ON rag."01_base_conhecimento_regras_geral" (document_hash);

-- Criar índice GIN para busca em JSONB
CREATE INDEX IF NOT EXISTS idx_base_conhecimento_conteudo 
ON rag."01_base_conhecimento_regras_geral" USING GIN (conteudo);

-- Configurar permissões
ALTER TABLE rag."01_base_conhecimento_regras_geral" OWNER TO postgres;

-- Garantir que o service role tem acesso
GRANT ALL ON SCHEMA rag TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA rag TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA rag TO postgres;

-- Função para verificar duplicatas (no schema public para acesso via API)
CREATE OR REPLACE FUNCTION public.check_duplicate_content(
    p_content_hash text,
    p_document_hash text
) RETURNS TABLE (
    is_exists boolean,
    existing_id uuid
) 
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        true as is_exists,
        id as existing_id
    FROM rag."01_base_conhecimento_regras_geral"
    WHERE content_hash = p_content_hash
        OR document_hash = p_document_hash
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT false, NULL::uuid;
    END IF;
END;
$$;

-- Função para inserir documento (no schema public para acesso via API)
CREATE OR REPLACE FUNCTION public.insert_document(
    p_data jsonb
) RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    v_id uuid;
BEGIN
    INSERT INTO rag."01_base_conhecimento_regras_geral" (
        version_key,
        titulo,
        conteudo,
        error_log,
        created_at,
        updated_at,
        processing_status,
        content_hash,
        last_embedding_update,
        embedding_attempts,
        metadata,
        document_hash
    )
    SELECT
        p_data->>'version_key',
        p_data->>'titulo',
        (p_data->>'conteudo')::jsonb,
        p_data->>'error_log',
        COALESCE((p_data->>'created_at')::timestamptz, now()),
        COALESCE((p_data->>'updated_at')::timestamptz, now()),
        p_data->>'processing_status',
        p_data->>'content_hash',
        (p_data->>'last_embedding_update')::timestamptz,
        COALESCE((p_data->>'embedding_attempts')::int, 0),
        (p_data->>'metadata')::jsonb,
        p_data->>'document_hash'
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$;