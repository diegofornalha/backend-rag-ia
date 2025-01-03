-- Remover funções existentes
DROP FUNCTION IF EXISTS executar_sql(text);
DROP FUNCTION IF EXISTS select_from_rag(text, integer);
DROP FUNCTION IF EXISTS insert_into_rag(text, json);
DROP FUNCTION IF EXISTS update_in_rag(text, text, json);
DROP FUNCTION IF EXISTS delete_from_rag(text, text);

-- Garantir acesso aos schemas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON TABLES TO postgres, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT SELECT ON TABLES TO anon;

-- Garantir acesso aos schemas
GRANT ALL ON SCHEMA public TO postgres, authenticated, service_role;
GRANT USAGE ON SCHEMA public TO anon;
GRANT ALL ON SCHEMA rag TO postgres, authenticated, service_role;
GRANT USAGE ON SCHEMA rag TO anon;

-- Garantir permissões nas tabelas existentes
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, authenticated, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA rag TO postgres, authenticated, service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA rag TO anon;

-- Garantir permissões em sequências
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA rag TO postgres, authenticated, service_role;

-- Criar função RPC para executar SQL
CREATE OR REPLACE FUNCTION executar_sql(sql text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    result jsonb;
BEGIN
    -- Executa a query e retorna o resultado como JSONB
    EXECUTE format('SELECT jsonb_agg(t) FROM (%s) t', sql) INTO result;
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$;

-- Garantir permissões na função
GRANT EXECUTE ON FUNCTION executar_sql(text) TO postgres, service_role;

-- Criar função RPC para acessar tabelas no schema rag
CREATE OR REPLACE FUNCTION select_from_rag(table_name text, limit_num integer DEFAULT 100)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    query text;
    result jsonb;
BEGIN
    -- Constrói a query dinamicamente
    query := format('SELECT * FROM rag."%s" LIMIT %s', table_name, limit_num);
    
    -- Executa a query e retorna o resultado como JSONB
    EXECUTE format('SELECT jsonb_agg(t) FROM (%s) t', query) INTO result;
    
    RETURN COALESCE(result, '[]'::jsonb);
END;
$$;

-- Criar função RPC para inserir nas tabelas do schema rag
CREATE OR REPLACE FUNCTION insert_into_rag(table_name text, data json)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    inserted_row jsonb;
BEGIN
    -- Insere os dados e retorna o resultado
    EXECUTE format(
        'INSERT INTO rag."%s" (
            version_key, 
            titulo, 
            conteudo, 
            error_log,
            metadata,
            document_hash,
            content_hash,
            processing_status,
            last_embedding_update,
            embedding_attempts
        ) VALUES (
            $1, $2, $3::json::jsonb, $4, $5::json::jsonb, $6, $7,
            COALESCE($8, ''pending''),
            COALESCE($9, CURRENT_TIMESTAMP),
            COALESCE($10, 0)
        ) RETURNING row_to_json("%s".*)::jsonb',
        table_name,
        table_name
    )
    USING 
        data->>'version_key',
        data->>'titulo',
        data->>'conteudo',
        data->>'error_log',
        data->>'metadata',
        data->>'document_hash',
        data->>'content_hash',
        data->>'processing_status',
        (data->>'last_embedding_update')::timestamp with time zone,
        (data->>'embedding_attempts')::integer
    INTO inserted_row;
    
    RETURN inserted_row;
END;
$$;

-- Criar função RPC para atualizar nas tabelas do schema rag
CREATE OR REPLACE FUNCTION update_in_rag(table_name text, version_key text, data json)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    updated_row jsonb;
BEGIN
    -- Atualiza os dados e retorna o resultado
    EXECUTE format(
        'UPDATE rag."%s" SET 
            titulo = COALESCE($1, titulo),
            conteudo = COALESCE($2::json::jsonb, conteudo),
            error_log = COALESCE($3, error_log),
            metadata = COALESCE($4::json::jsonb, metadata),
            document_hash = COALESCE($5, document_hash),
            content_hash = COALESCE($6, content_hash),
            processing_status = COALESCE($7, processing_status),
            last_embedding_update = COALESCE($8, last_embedding_update),
            embedding_attempts = COALESCE($9, embedding_attempts)
        WHERE version_key = $10
        RETURNING row_to_json("%s".*)::jsonb',
        table_name,
        table_name
    )
    USING 
        data->>'titulo',
        data->>'conteudo',
        data->>'error_log',
        data->>'metadata',
        data->>'document_hash',
        data->>'content_hash',
        data->>'processing_status',
        (data->>'last_embedding_update')::timestamp with time zone,
        (data->>'embedding_attempts')::integer,
        version_key
    INTO updated_row;
    
    RETURN COALESCE(updated_row, '{}'::jsonb);
END;
$$;

-- Criar função RPC para deletar nas tabelas do schema rag
CREATE OR REPLACE FUNCTION delete_from_rag(table_name text, version_key text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    deleted_row jsonb;
BEGIN
    -- Deleta os dados e retorna o resultado
    EXECUTE format(
        'DELETE FROM rag."%s" 
        WHERE version_key = $1
        RETURNING row_to_json("%s".*)::jsonb',
        table_name,
        table_name
    )
    USING version_key
    INTO deleted_row;
    
    RETURN COALESCE(deleted_row, '{}'::jsonb);
END;
$$;

-- Conceder acesso às funções
GRANT EXECUTE ON FUNCTION select_from_rag(text, integer) TO authenticated, anon;
GRANT EXECUTE ON FUNCTION insert_into_rag(text, json) TO authenticated;
GRANT EXECUTE ON FUNCTION update_in_rag(text, text, json) TO service_role;
GRANT EXECUTE ON FUNCTION delete_from_rag(text, text) TO service_role; 