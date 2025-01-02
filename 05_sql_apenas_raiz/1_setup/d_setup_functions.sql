-- Função para inserir embeddings
CREATE OR REPLACE FUNCTION rag.insert_embedding(
    p_documento_id UUID,
    p_embedding FLOAT[],
    p_modelo TEXT DEFAULT 'all-MiniLM-L6-v2',
    p_content_hash TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO rag."02_embeddings_regras_geral" (
        documento_id, 
        embedding, 
        modelo,
        content_hash,
        processing_status,
        last_embedding_update,
        embedding_attempts
    )
    VALUES (
        p_documento_id, 
        p_embedding::vector(384), 
        p_modelo,
        p_content_hash,
        'completed',
        CURRENT_TIMESTAMP,
        1
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 

-- Função para inserir embeddings via RPC
CREATE OR REPLACE FUNCTION rag.insert_embedding_rpc(
    doc_id UUID,
    embedding_array TEXT,
    content_hash TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO rag."02_embeddings_regras_geral" (
        documento_id, 
        embedding,
        content_hash,
        processing_status,
        last_embedding_update,
        embedding_attempts
    )
    VALUES (
        doc_id,
        embedding_array::vector(384),
        content_hash,
        'completed',
        CURRENT_TIMESTAMP,
        1
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 

-- Função para atualizar status do embedding
CREATE OR REPLACE FUNCTION rag.update_embedding_status(
    p_embedding_id UUID,
    p_status TEXT,
    p_error_log JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    UPDATE rag."02_embeddings_regras_geral"
    SET 
        processing_status = p_status,
        embedding_attempts = embedding_attempts + 1,
        last_embedding_update = CURRENT_TIMESTAMP
    WHERE id = p_embedding_id;
    
    IF p_error_log IS NOT NULL THEN
        UPDATE rag."01_base_conhecimento_regras_geral" d
        SET error_log = error_log || p_error_log
        FROM rag."02_embeddings_regras_geral" e
        WHERE e.id = p_embedding_id
        AND e.documento_id = d.id;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 