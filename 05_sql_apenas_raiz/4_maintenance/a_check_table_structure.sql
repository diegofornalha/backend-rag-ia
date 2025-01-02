-- Verificar estrutura da tabela
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'rag'
AND table_name = '01_base_conhecimento_regras_geral'
ORDER BY ordinal_position; 