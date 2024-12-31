-- Função para inserir embeddings
CREATE OR REPLACE FUNCTION rag.insert_embedding(
    p_documento_id UUID,
    p_embedding FLOAT[],
    p_modelo TEXT DEFAULT 'all-MiniLM-L6-v2'
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO rag."02_embeddings_regras_geral" (documento_id, embedding, modelo)
    VALUES (p_documento_id, p_embedding::vector(384), p_modelo)
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 

-- Função para inserir embeddings via RPC
CREATE OR REPLACE FUNCTION rag.insert_embedding_rpc(
    doc_id UUID,
    embedding_array TEXT
) RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    -- Converte o texto do array para vector
    INSERT INTO rag."02_embeddings_regras_geral" (documento_id, embedding)
    VALUES (
        doc_id,
        embedding_array::vector(384)
    )
    RETURNING id INTO v_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 