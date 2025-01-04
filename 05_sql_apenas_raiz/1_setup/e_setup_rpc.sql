-- Criar função RPC para acessar tabelas no schema rag
CREATE OR REPLACE FUNCTION select_from_rag(table_name text, limit_num integer)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, public
AS $$
DECLARE
    query text;
    result json;
BEGIN
    -- Constrói a query dinamicamente
    query := format('SELECT * FROM rag.%I LIMIT %s', table_name, limit_num);
    
    -- Executa a query e retorna o resultado como JSON
    EXECUTE format('SELECT json_agg(t) FROM (%s) t', query) INTO result;
    
    RETURN COALESCE(result, '[]'::json);
END;
$$; 