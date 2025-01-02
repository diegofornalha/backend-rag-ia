-- Criar extensão se não existir
CREATE EXTENSION IF NOT EXISTS vector;

-- Criar tabela
CREATE TABLE IF NOT EXISTS rag."02_embeddings_regras_geral" (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    document_id uuid REFERENCES rag."01_base_conhecimento_regras_geral"(id) ON DELETE CASCADE,
    embedding vector(1536),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_02_embeddings_regras_geral_document_id 
ON rag."02_embeddings_regras_geral"(document_id);

-- Criar trigger para atualizar updated_at
DROP TRIGGER IF EXISTS update_02_embeddings_regras_geral_updated_at 
ON rag."02_embeddings_regras_geral";

CREATE TRIGGER update_02_embeddings_regras_geral_updated_at
    BEFORE UPDATE ON rag."02_embeddings_regras_geral"
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();

-- Conceder permissões
GRANT ALL ON TABLE rag."02_embeddings_regras_geral" TO postgres, service_role;
GRANT SELECT ON TABLE rag."02_embeddings_regras_geral" TO authenticated;
GRANT SELECT ON TABLE rag."02_embeddings_regras_geral" TO anon; 