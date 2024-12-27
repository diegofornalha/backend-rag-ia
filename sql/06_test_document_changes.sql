-- Limpar logs anteriores
TRUNCATE document_changes_log;

-- Verificar contagem inicial
SELECT 'Contagem Inicial' as step,
       (SELECT COUNT(*) FROM documents) as documents_count,
       (SELECT value FROM statistics WHERE key = 'documents_count') as stored_count;

-- Inserir documento de teste
INSERT INTO documents (content, metadata)
VALUES ('Documento de teste 1', '{"title": "Teste 1"}')
RETURNING id;

-- Verificar após inserção
SELECT 'Após Inserção' as step,
       (SELECT COUNT(*) FROM documents) as documents_count,
       (SELECT value FROM statistics WHERE key = 'documents_count') as stored_count;

-- Verificar log de alteração
SELECT 'Log da Inserção' as step,
       operation,
       document_id,
       previous_count,
       new_count,
       changed_at
FROM document_changes_log
ORDER BY changed_at DESC
LIMIT 1;

-- Deletar documento
DELETE FROM documents 
WHERE content = 'Documento de teste 1'
RETURNING id;

-- Verificar após deleção
SELECT 'Após Deleção' as step,
       (SELECT COUNT(*) FROM documents) as documents_count,
       (SELECT value FROM statistics WHERE key = 'documents_count') as stored_count;

-- Verificar histórico completo
SELECT 'Histórico de Alterações' as step;
SELECT * FROM get_document_changes_history(1);  -- última hora

-- Verificar consistência
SELECT 
    'Verificação Final' as step,
    CASE 
        WHEN (SELECT COUNT(*) FROM documents) = 
             (SELECT value FROM statistics WHERE key = 'documents_count')
        THEN 'OK: Contagens sincronizadas'
        ELSE 'ERRO: Contagens diferentes'
    END as status,
    (SELECT COUNT(*) FROM documents) as real_count,
    (SELECT value FROM statistics WHERE key = 'documents_count') as stored_count; 