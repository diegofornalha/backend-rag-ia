-- Script para backup usando SQL puro
DO $$
DECLARE
    table_exists boolean;
BEGIN
    -- Notificar início
    RAISE NOTICE 'Iniciando backup das tabelas...';
    
    -- Backup da tabela base_conhecimento
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'rag' 
        AND table_name = '01_base_conhecimento_regras_geral'
    ) INTO table_exists;
    
    IF table_exists THEN
        CREATE TEMP TABLE temp_base_conhecimento AS 
        SELECT * FROM rag."01_base_conhecimento_regras_geral";
        RAISE NOTICE 'Backup de 01_base_conhecimento_regras_geral concluído';
    ELSE
        RAISE NOTICE 'Tabela 01_base_conhecimento_regras_geral não existe - pulando';
    END IF;
    
    -- Backup da tabela embeddings
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'rag' 
        AND table_name = '02_embeddings_regras_geral'
    ) INTO table_exists;
    
    IF table_exists THEN
        CREATE TEMP TABLE temp_embeddings AS 
        SELECT * FROM rag."02_embeddings_regras_geral";
        RAISE NOTICE 'Backup de 02_embeddings_regras_geral concluído';
    ELSE
        RAISE NOTICE 'Tabela 02_embeddings_regras_geral não existe - pulando';
    END IF;
    
    -- Backup da tabela rule_counts
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'rules' 
        AND table_name = 'rule_counts'
    ) INTO table_exists;
    
    IF table_exists THEN
        CREATE TEMP TABLE temp_rule_counts AS 
        SELECT * FROM rules.rule_counts;
        RAISE NOTICE 'Backup de rule_counts concluído';
    ELSE
        RAISE NOTICE 'Tabela rule_counts não existe - pulando';
    END IF;
    
    -- Notificar conclusão
    RAISE NOTICE 'Backup em tabelas temporárias concluído!';
END $$;

-- Para visualizar os backups (use apenas para as tabelas que existem):
-- SELECT * FROM temp_base_conhecimento;
-- SELECT * FROM temp_embeddings;
-- SELECT * FROM temp_rule_counts; 