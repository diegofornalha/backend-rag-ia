-- Função para verificar e corrigir contagem
CREATE OR REPLACE FUNCTION sync_documents_count()
RETURNS void AS $$
DECLARE
    real_count integer;
BEGIN
    -- Pega contagem real
    SELECT COUNT(*) INTO real_count FROM documents;
    
    -- Atualiza statistics
    UPDATE statistics 
    SET value = real_count,
        updated_at = NOW()
    WHERE key = 'documents_count';
    
    -- Se não existir, insere
    IF NOT FOUND THEN
        INSERT INTO statistics (key, value, updated_at)
        VALUES ('documents_count', real_count, NOW());
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Função para testar contagem
CREATE OR REPLACE FUNCTION test_documents_count()
RETURNS TABLE (
    test_name text,
    result boolean,
    details text
) AS $$
BEGIN
    -- Teste 1: Verificar se existe registro na tabela statistics
    RETURN QUERY
    SELECT 
        'Existe registro de contagem'::text,
        EXISTS (SELECT 1 FROM statistics WHERE key = 'documents_count'),
        CASE 
            WHEN EXISTS (SELECT 1 FROM statistics WHERE key = 'documents_count')
            THEN 'OK: Registro encontrado'
            ELSE 'ERRO: Registro não encontrado'
        END;

    -- Teste 2: Verificar se contagem está correta
    RETURN QUERY
    SELECT 
        'Contagem está correta'::text,
        (SELECT COUNT(*) FROM documents) = (SELECT value FROM statistics WHERE key = 'documents_count'),
        'Real: ' || (SELECT COUNT(*)::text FROM documents) || 
        ' / Armazenado: ' || COALESCE((SELECT value::text FROM statistics WHERE key = 'documents_count'), 'NULL');

    -- Teste 3: Verificar última atualização
    RETURN QUERY
    SELECT 
        'Última atualização recente'::text,
        COALESCE((SELECT updated_at > NOW() - INTERVAL '1 hour' FROM statistics WHERE key = 'documents_count'), false),
        'Última atualização: ' || COALESCE((SELECT updated_at::text FROM statistics WHERE key = 'documents_count'), 'Nunca');
END;
$$ LANGUAGE plpgsql;

-- Executar testes
SELECT * FROM test_documents_count();

-- Atualizar contagem manualmente (exemplo)
UPDATE statistics 
SET value = 5, 
    updated_at = NOW() 
WHERE key = 'documents_count';

-- Verificar após atualização manual
SELECT * FROM test_documents_count();

-- Sincronizar contagem
SELECT sync_documents_count();

-- Verificar após sincronização
SELECT * FROM test_documents_count(); 