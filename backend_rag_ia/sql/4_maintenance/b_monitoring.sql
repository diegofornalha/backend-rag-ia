-- Analisar estrutura das tabelas
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_schema = 'rag'
    AND table_name IN ('01_base_conhecimento_regras_geral', '02_embeddings_regras_geral')
ORDER BY 
    table_name, ordinal_position;

-- Contar registros em cada tabela
SELECT '01_base_conhecimento_regras_geral' as tabela, COUNT(*) as total 
FROM rag."01_base_conhecimento_regras_geral"
UNION ALL
SELECT '02_embeddings_regras_geral' as tabela, COUNT(*) as total 
FROM rag."02_embeddings_regras_geral";

-- Verificar índices
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    schemaname = 'rag'
    AND tablename IN ('01_base_conhecimento_regras_geral', '02_embeddings_regras_geral')
ORDER BY
    tablename, indexname;

-- Verificar constraints
SELECT 
    tc.table_schema,
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM 
    information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
WHERE 
    tc.table_schema = 'rag'
    AND tc.table_name IN ('01_base_conhecimento_regras_geral', '02_embeddings_regras_geral')
ORDER BY
    tc.table_name, tc.constraint_name;

-- Verificar políticas RLS
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM 
    pg_policies
WHERE 
    schemaname = 'rag'
    AND tablename IN ('01_base_conhecimento_regras_geral', '02_embeddings_regras_geral')
ORDER BY
    tablename, policyname;

-- Verificar triggers
SELECT 
    trigger_schema,
    trigger_name,
    event_manipulation,
    event_object_schema,
    event_object_table,
    action_statement,
    action_timing
FROM 
    information_schema.triggers
WHERE 
    event_object_schema = 'rag'
    AND event_object_table IN ('01_base_conhecimento_regras_geral', '02_embeddings_regras_geral')
ORDER BY
    event_object_table, trigger_name; 