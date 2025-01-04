-- Criar enum para tipos de operação
CREATE TYPE rag.operation_type AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE',
    'EMBEDDING_GENERATED',
    'ERROR',
    'SYSTEM_UPDATE'
);

-- Criar tabela de changelog
CREATE TABLE IF NOT EXISTS rag.changelog (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_type rag.operation_type NOT NULL,
    table_name text NOT NULL,
    record_id text NOT NULL,
    old_data jsonb,
    new_data jsonb,
    error_details text,
    user_id uuid,
    ip_address text,
    created_at timestamptz DEFAULT now()
);

-- Criar índices para melhor performance em consultas comuns
CREATE INDEX IF NOT EXISTS idx_changelog_operation_type ON rag.changelog(operation_type);
CREATE INDEX IF NOT EXISTS idx_changelog_table_name ON rag.changelog(table_name);
CREATE INDEX IF NOT EXISTS idx_changelog_created_at ON rag.changelog(created_at);
CREATE INDEX IF NOT EXISTS idx_changelog_record_id ON rag.changelog(record_id);

-- Função para registrar mudanças
CREATE OR REPLACE FUNCTION rag.log_change(
    p_operation_type rag.operation_type,
    p_table_name text,
    p_record_id text,
    p_old_data jsonb DEFAULT NULL,
    p_new_data jsonb DEFAULT NULL,
    p_error_details text DEFAULT NULL,
    p_user_id uuid DEFAULT NULL,
    p_ip_address text DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
    v_changelog_id uuid;
BEGIN
    INSERT INTO rag.changelog (
        operation_type,
        table_name,
        record_id,
        old_data,
        new_data,
        error_details,
        user_id,
        ip_address
    ) VALUES (
        p_operation_type,
        p_table_name,
        p_record_id,
        p_old_data,
        p_new_data,
        p_error_details,
        p_user_id,
        p_ip_address
    )
    RETURNING id INTO v_changelog_id;

    RETURN v_changelog_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função trigger para registrar mudanças automaticamente
CREATE OR REPLACE FUNCTION rag.trigger_log_changes()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM rag.log_change(
            'INSERT'::rag.operation_type,
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            NEW.id::text,
            NULL,
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM rag.log_change(
            'UPDATE'::rag.operation_type,
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            NEW.id::text,
            to_jsonb(OLD),
            to_jsonb(NEW)
        );
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM rag.log_change(
            'DELETE'::rag.operation_type,
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            OLD.id::text,
            to_jsonb(OLD),
            NULL
        );
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Adicionar triggers nas tabelas principais
DROP TRIGGER IF EXISTS log_changes_01 ON rag."01_base_conhecimento_regras_geral";
CREATE TRIGGER log_changes_01
    AFTER INSERT OR UPDATE OR DELETE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.trigger_log_changes();

DROP TRIGGER IF EXISTS log_changes_02 ON rag."02_embeddings_regras_geral";
CREATE TRIGGER log_changes_02
    AFTER INSERT OR UPDATE OR DELETE ON rag."02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION rag.trigger_log_changes();

-- Garantir permissões
GRANT ALL ON TABLE rag.changelog TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION rag.log_change(rag.operation_type, text, text, jsonb, jsonb, text, uuid, text) TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION rag.trigger_log_changes() TO postgres, anon, authenticated, service_role; 