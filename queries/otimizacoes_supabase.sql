-- Criar view materializada para consultas frequentes
CREATE MATERIALIZED VIEW rag.view_documentos_frequentes AS
SELECT id, titulo, conteudo, embedding
FROM rag.01
WHERE acesso_count > 10;

-- Criar índice para busca eficiente
CREATE INDEX idx_documentos_acesso 
ON rag.01 (acesso_count DESC);

-- Refresh programado da view
REFRESH MATERIALIZED VIEW rag.view_documentos_frequentes; 