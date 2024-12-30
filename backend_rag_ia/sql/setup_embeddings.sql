-- Função para deletar embeddings quando um documento é removido
CREATE OR REPLACE FUNCTION delete_document_embeddings()
RETURNS TRIGGER AS $$
BEGIN
    -- Deleta os embeddings associados ao documento
    DELETE FROM embeddings WHERE document_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger que é acionado antes de deletar um documento
DROP TRIGGER IF EXISTS trigger_delete_document_embeddings ON documents;
CREATE TRIGGER trigger_delete_document_embeddings
    BEFORE DELETE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION delete_document_embeddings();

-- Função para verificar integridade
CREATE OR REPLACE FUNCTION check_document_embedding_integrity()
RETURNS TABLE (
    documents_count bigint,
    embeddings_count bigint,
    orphaned_embeddings bigint,
    documents_without_embeddings bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        (SELECT COUNT(*) FROM documents) as documents_count,
        (SELECT COUNT(*) FROM embeddings) as embeddings_count,
        (SELECT COUNT(*) 
         FROM embeddings e 
         LEFT JOIN documents d ON e.document_id = d.id 
         WHERE d.id IS NULL) as orphaned_embeddings,
        (SELECT COUNT(*) 
         FROM documents d 
         LEFT JOIN embeddings e ON d.id = e.document_id 
         WHERE e.id IS NULL) as documents_without_embeddings;
END;
$$ LANGUAGE plpgsql; 