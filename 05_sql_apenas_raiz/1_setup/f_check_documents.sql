-- Função para contar documentos na tabela 01
CREATE OR REPLACE FUNCTION public.count_documents()
RETURNS TABLE (
    total_documents bigint,
    documents_with_embeddings bigint,
    documents_without_embeddings bigint
) AS $$
BEGIN
    RETURN QUERY
    WITH counts AS (
        SELECT 
            COUNT(*) as total,
            COUNT(e.id) as with_embeddings
        FROM rag."01_base_conhecimento_regras_geral" d
        LEFT JOIN rag."02_embeddings_regras_geral" e ON e.document_id = d.id
    )
    SELECT 
        total as total_documents,
        with_embeddings as documents_with_embeddings,
        (total - with_embeddings) as documents_without_embeddings
    FROM counts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Garantir permissões
GRANT EXECUTE ON FUNCTION public.count_documents() TO postgres, anon, authenticated, service_role; 