-- Cria função para inserir embeddings
CREATE OR REPLACE FUNCTION rag.insert_embedding(
    p_document_id uuid,
    p_embedding vector(1536),
    p_content_hash text
) RETURNS uuid AS $$
DECLARE
    v_id uuid;
BEGIN
    -- Insere o embedding
    INSERT INTO rag."02_embeddings_regras_geral" (
        document_id,
        embedding,
        content_hash,
        processing_status,
        last_embedding_update
    ) VALUES (
        p_document_id,
        p_embedding,
        p_content_hash,
        'completed',
        timezone('utc'::text, now())
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Cria função para atualizar embeddings
CREATE OR REPLACE FUNCTION rag.update_embedding(
    p_document_id uuid,
    p_embedding vector(1536),
    p_content_hash text
) RETURNS void AS $$
BEGIN
    -- Atualiza o embedding
    UPDATE rag."02_embeddings_regras_geral"
    SET 
        embedding = p_embedding,
        content_hash = p_content_hash,
        processing_status = 'completed',
        last_embedding_update = timezone('utc'::text, now()),
        embedding_attempts = embedding_attempts + 1
    WHERE document_id = p_document_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 