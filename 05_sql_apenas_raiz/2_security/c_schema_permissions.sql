-- Garantir que o schema rag existe
CREATE SCHEMA IF NOT EXISTS rag;

-- Conceder permissões ao schema rag
GRANT USAGE ON SCHEMA rag TO postgres, anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA rag TO postgres, service_role;
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA rag TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA rag TO anon;

-- Configurar permissões padrão para novas tabelas
ALTER DEFAULT PRIVILEGES IN SCHEMA rag
GRANT ALL ON TABLES TO postgres, service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
GRANT SELECT, INSERT ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA rag
GRANT SELECT ON TABLES TO anon;

-- Garantir que o PostgREST pode acessar o schema
ALTER ROLE authenticator SET search_path = rag, public, extensions;
ALTER ROLE postgres SET search_path = rag, public, extensions;

-- Atualizar as permissões nas tabelas existentes
GRANT ALL ON TABLE rag.01_base_conhecimento_regras_geral TO postgres, service_role;
GRANT SELECT, INSERT ON TABLE rag.01_base_conhecimento_regras_geral TO authenticated;
GRANT SELECT ON TABLE rag.01_base_conhecimento_regras_geral TO anon;

GRANT ALL ON TABLE rag.02_embeddings_regras_geral TO postgres, service_role;
GRANT SELECT ON TABLE rag.02_embeddings_regras_geral TO authenticated;
GRANT SELECT ON TABLE rag.02_embeddings_regras_geral TO anon; 