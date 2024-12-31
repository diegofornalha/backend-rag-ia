-- Função para deletar embeddings quando um documento da base de conhecimento é removido
CREATE OR REPLACE FUNCTION delete_document_embeddings()
RETURNS TRIGGER AS $$
BEGIN
    -- Deleta os embeddings associados ao documento da base de conhecimento
    DELETE FROM "02_embeddings_regras_geral" WHERE documento_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger que é acionado antes de deletar um documento da base de conhecimento
DROP TRIGGER IF EXISTS trigger_delete_document_embeddings ON "01_base_conhecimento_regras_geral";
CREATE TRIGGER trigger_delete_document_embeddings
    BEFORE DELETE ON "01_base_conhecimento_regras_geral"
    FOR EACH ROW
    EXECUTE FUNCTION delete_document_embeddings();

-- Função para verificar integridade entre base de conhecimento e embeddings
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
        (SELECT COUNT(*) FROM "01_base_conhecimento_regras_geral") as documents_count,
        (SELECT COUNT(*) FROM "02_embeddings_regras_geral") as embeddings_count,
        (SELECT COUNT(*) 
         FROM "02_embeddings_regras_geral" e 
         LEFT JOIN "01_base_conhecimento_regras_geral" d ON e.documento_id = d.id 
         WHERE d.id IS NULL) as orphaned_embeddings,
        (SELECT COUNT(*) 
         FROM "01_base_conhecimento_regras_geral" d 
         LEFT JOIN "02_embeddings_regras_geral" e ON d.id = e.documento_id 
         WHERE e.id IS NULL) as documents_without_embeddings;
END;
$$ LANGUAGE plpgsql;

-- Função para gerar embeddings usando OpenAI
CREATE OR REPLACE FUNCTION generate_embedding(input_text TEXT)
RETURNS vector
LANGUAGE plpgsql
AS $$
DECLARE
    embedding_vector vector;
BEGIN
    -- Call the OpenAI API to generate embeddings
    SELECT embedding INTO embedding_vector
    FROM openai.embeddings(
        input_text,  -- text to generate embedding for
        'text-embedding-ada-002'  -- model to use
    );
    
    RETURN embedding_vector;
END;
$$; 