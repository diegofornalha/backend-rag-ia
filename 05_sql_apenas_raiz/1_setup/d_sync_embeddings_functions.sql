-- Função para buscar documentos sem embeddings (no schema public)
CREATE OR REPLACE FUNCTION public.get_documents_without_embeddings()
RETURNS TABLE (
    id uuid,
    conteudo jsonb,
    content_hash text
) AS $$
BEGIN
    RETURN QUERY
    SELECT d.id, d.conteudo, d.content_hash
    FROM rag."01" d
    LEFT JOIN rag."02" e ON e.document_id = d.id
    WHERE e.document_id IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para salvar embedding de um documento (no schema public)
CREATE OR REPLACE FUNCTION public.save_document_embedding(
    p_document_id uuid,
    p_embedding vector,
    p_content_hash text,
    p_created_at timestamp with time zone,
    p_updated_at timestamp with time zone
) RETURNS void AS $$
BEGIN
    INSERT INTO rag."02" (
        document_id,
        embedding,
        content_hash,
        created_at,
        updated_at,
        processing_status,
        last_embedding_update,
        embedding_attempts
    ) VALUES (
        p_document_id,
        p_embedding,
        p_content_hash,
        p_created_at,
        p_updated_at,
        'completed',
        p_updated_at,
        1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para atualizar erro em um documento (no schema public)
CREATE OR REPLACE FUNCTION public.update_document_error(
    p_document_id uuid,
    p_error_log text,
    p_updated_at timestamp with time zone
) RETURNS void AS $$
BEGIN
    UPDATE rag."01"
    SET error_log = p_error_log,
        updated_at = p_updated_at
    WHERE id = p_document_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Garantir permissões
GRANT EXECUTE ON FUNCTION public.get_documents_without_embeddings() TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.save_document_embedding(uuid, vector, text, timestamp with time zone, timestamp with time zone) TO postgres, anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.update_document_error(uuid, text, timestamp with time zone) TO postgres, anon, authenticated, service_role; 