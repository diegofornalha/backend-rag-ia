-- Criar tabela de estatísticas no schema rag
CREATE TABLE IF NOT EXISTS rag.statistics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    key text NOT NULL UNIQUE,
    value int4 DEFAULT 0,
    updated_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

-- Função para atualizar estatísticas
CREATE OR REPLACE FUNCTION rag.update_statistics()
RETURNS void AS $$
BEGIN
    -- Inserir ou atualizar contagem de documentos
    INSERT INTO rag.statistics (key, value, updated_at)
    VALUES (
        'documents_count',
        (SELECT COUNT(*) FROM rag."01_base_conhecimento_regras_geral"),
        now()
    )
    ON CONFLICT (key)
    DO UPDATE SET 
        value = EXCLUDED.value,
        updated_at = EXCLUDED.updated_at;

    -- Inserir ou atualizar contagem de embeddings
    INSERT INTO rag.statistics (key, value, updated_at)
    VALUES (
        'embeddings_count',
        (SELECT COUNT(*) FROM rag."02_embeddings_regras_geral"),
        now()
    )
    ON CONFLICT (key)
    DO UPDATE SET 
        value = EXCLUDED.value,
        updated_at = EXCLUDED.updated_at;

    -- Inserir ou atualizar documentos sem embeddings
    INSERT INTO rag.statistics (key, value, updated_at)
    VALUES (
        'documents_without_embeddings',
        (
            SELECT COUNT(*)
            FROM rag."01_base_conhecimento_regras_geral" d
            LEFT JOIN rag."02_embeddings_regras_geral" e ON e.document_id = d.id
            WHERE e.id IS NULL
        ),
        now()
    )
    ON CONFLICT (key)
    DO UPDATE SET 
        value = EXCLUDED.value,
        updated_at = EXCLUDED.updated_at;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Criar trigger para atualizar estatísticas automaticamente
CREATE OR REPLACE FUNCTION rag.trigger_update_statistics()
RETURNS trigger AS $$
BEGIN
    PERFORM rag.update_statistics();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Adicionar triggers nas tabelas principais
DROP TRIGGER IF EXISTS update_statistics_01 ON rag."01_base_conhecimento_regras_geral";
CREATE TRIGGER update_statistics_01
    AFTER INSERT OR UPDATE OR DELETE ON rag."01_base_conhecimento_regras_geral"
    FOR EACH STATEMENT
    EXECUTE FUNCTION rag.trigger_update_statistics();

DROP TRIGGER IF EXISTS update_statistics_02 ON rag."02_embeddings_regras_geral";
CREATE TRIGGER update_statistics_02
    AFTER INSERT OR UPDATE OR DELETE ON rag."02_embeddings_regras_geral"
    FOR EACH STATEMENT
    EXECUTE FUNCTION rag.trigger_update_statistics();

-- Garantir permissões
GRANT ALL ON TABLE rag.statistics TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION rag.update_statistics() TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION rag.trigger_update_statistics() TO postgres, anon, authenticated, service_role;

-- Inicializar estatísticas
SELECT rag.update_statistics(); 