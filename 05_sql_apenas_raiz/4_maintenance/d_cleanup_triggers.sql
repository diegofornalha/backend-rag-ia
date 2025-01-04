-- Remover triggers duplicados
DROP TRIGGER IF EXISTS trigger_update_timestamp ON rag."01_base_conhecimento_regras_geral";
DROP TRIGGER IF EXISTS update_embeddings_regras_updated_at ON rag."02_embeddings_regras_geral";

-- Remover função antiga se existir
DROP FUNCTION IF EXISTS update_updated_at();

-- Verificar se os triggers corretos ainda existem
DO $$
BEGIN
    -- Para a tabela base_conhecimento
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'update_base_conhecimento_updated_at'
        AND event_object_schema = 'rag'
        AND event_object_table = '01_base_conhecimento_regras_geral'
    ) THEN
        CREATE TRIGGER update_base_conhecimento_updated_at
        BEFORE UPDATE ON rag."01_base_conhecimento_regras_geral"
        FOR EACH ROW
        EXECUTE FUNCTION rag.update_updated_at_column();
    END IF;

    -- Para a tabela embeddings
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.triggers 
        WHERE trigger_name = 'update_embeddings_updated_at'
        AND event_object_schema = 'rag'
        AND event_object_table = '02_embeddings_regras_geral'
    ) THEN
        CREATE TRIGGER update_embeddings_updated_at
        BEFORE UPDATE ON rag."02_embeddings_regras_geral"
        FOR EACH ROW
        EXECUTE FUNCTION rag.update_updated_at_column();
    END IF;
END $$; 