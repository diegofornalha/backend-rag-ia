-- Script para limpar referências antigas
DO $$
BEGIN
    -- Remove tabelas antigas e suas dependências
    DROP TABLE IF EXISTS documents CASCADE;
    DROP TABLE IF EXISTS documentos CASCADE;
    DROP TABLE IF EXISTS embeddings CASCADE;
    
    -- Remove funções antigas
    DROP FUNCTION IF EXISTS delete_document_embeddings_old();
    DROP FUNCTION IF EXISTS check_documents_integrity();
    DROP FUNCTION IF EXISTS match_documents(vector, float, int);
    
    RAISE NOTICE 'Limpeza concluída';
END;
$$; 