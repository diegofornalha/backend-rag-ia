-- Analisar estrutura das tabelas
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    column_default,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name IN ('documentos', 'documents')
    AND table_schema = 'public'
ORDER BY 
    table_name, ordinal_position;

-- Contar registros em cada tabela
SELECT 'documentos' as tabela, COUNT(*) as total FROM public.documentos
UNION ALL
SELECT 'documents' as tabela, COUNT(*) as total FROM public.documents;

-- Verificar índices
SELECT
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    tablename IN ('documentos', 'documents')
    AND schemaname = 'public';

-- Verificar constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    kcu.column_name
FROM 
    information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
WHERE 
    tc.table_name IN ('documentos', 'documents')
    AND tc.table_schema = 'public';

-- Verificar políticas RLS
SELECT 
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
    tablename IN ('documentos', 'documents'); 