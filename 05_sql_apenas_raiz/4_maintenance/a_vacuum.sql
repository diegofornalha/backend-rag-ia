-- Remover funções existentes
DROP FUNCTION IF EXISTS cleanup_old_documents(integer) CASCADE;
DROP FUNCTION IF EXISTS cleanup_orphaned_embeddings() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at() CASCADE;

-- Função para limpar documentos antigos
CREATE OR REPLACE FUNCTION cleanup_old_documents(days_old integer)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    deleted_count integer;
BEGIN
    DELETE FROM rag."01_base_conhecimento_regras_geral"
    WHERE created_at < NOW() - (days_old || ' days')::interval;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Função para limpar embeddings órfãos
CREATE OR REPLACE FUNCTION cleanup_orphaned_embeddings()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    deleted_count integer;
BEGIN
    DELETE FROM rag."02_embeddings_regras_geral" e
    WHERE NOT EXISTS (
        SELECT 1
        FROM rag."01_base_conhecimento_regras_geral" d
        WHERE d.id = e.documento_id
    );
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

-- Trigger para atualizar timestamp
DROP TRIGGER IF EXISTS trigger_update_timestamp ON rag."01_base_conhecimento_regras_geral";
CREATE TRIGGER trigger_update_timestamp
    BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at(); 