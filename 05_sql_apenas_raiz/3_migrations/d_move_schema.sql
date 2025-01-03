-- Criar novo schema se não existir
CREATE SCHEMA IF NOT EXISTS analytics;

-- Função para mover tabela entre schemas de forma segura
CREATE OR REPLACE FUNCTION move_table_to_schema(
    p_table_name text,
    p_from_schema text,
    p_to_schema text
) RETURNS void AS $$
BEGIN
    -- Verificar se a tabela existe no schema de origem
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = p_from_schema
        AND table_name = p_table_name
    ) THEN
        RAISE EXCEPTION 'Tabela %.% não existe', p_from_schema, p_table_name;
    END IF;

    -- Verificar se o schema de destino existe
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = p_to_schema
    ) THEN
        RAISE EXCEPTION 'Schema % não existe', p_to_schema;
    END IF;

    -- Mover a tabela
    EXECUTE format('ALTER TABLE %I.%I SET SCHEMA %I',
        p_from_schema, p_table_name, p_to_schema);

    -- Atualizar as políticas RLS se existirem
    -- As políticas precisam ser recriadas no novo schema
    
    RAISE NOTICE 'Tabela %.% movida com sucesso para schema %',
        p_from_schema, p_table_name, p_to_schema;
END;
$$ LANGUAGE plpgsql;

-- Exemplo de uso:
-- SELECT move_table_to_schema('nome_da_tabela', 'public', 'analytics');

-- Verificar tabelas em cada schema:
-- SELECT schemaname, tablename 
-- FROM pg_tables 
-- WHERE schemaname IN ('public', 'analytics')
-- ORDER BY schemaname, tablename; 