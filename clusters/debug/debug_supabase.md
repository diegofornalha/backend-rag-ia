# Debug Supabase

## Status Atual

### Monitoramento Ativo

🔄 Monitor ativado e aguardando deploy...

```bash
python monitor.py  # Monitorando status da API
```

### Verificação de Sincronização

1. Verificar Relação Documentos-Embeddings

```sql
-- Verificar documentos sem embeddings
SELECT d.id as document_id, d.content, d.created_at
FROM documents d
LEFT JOIN embeddings e ON d.id = e.document_id
WHERE e.id IS NULL;

-- Verificar embeddings órfãos (sem documento)
SELECT e.id as embedding_id, e.created_at
FROM embeddings e
LEFT JOIN documents d ON e.document_id = d.id
WHERE d.id IS NULL;

-- Comparar contagens
SELECT
    (SELECT COUNT(*) FROM documents) as total_documents,
    (SELECT COUNT(*) FROM embeddings) as total_embeddings;
```

2. Teste de Deleção

```bash
# Deletar todos os documentos
curl -X DELETE https://backend-rag-ia.onrender.com/api/v1/documents-all

# Verificar se embeddings foram deletados
SELECT COUNT(*) FROM embeddings;
```

3. Teste de Adição

```bash
# Adicionar novo documento
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "content": "Teste de sincronização doc-embedding",
    "metadata": {
      "title": "Teste Sync",
      "document_hash": "teste_sync_1"
    }
  }' \
  https://backend-rag-ia.onrender.com/api/v1/documents/

# Verificar criação do embedding
SELECT
    d.id as doc_id,
    e.id as emb_id,
    d.created_at as doc_created,
    e.created_at as emb_created
FROM documents d
LEFT JOIN embeddings e ON d.id = e.document_id
ORDER BY d.created_at DESC
LIMIT 1;
```

### Checklist de Sincronização

- [ ] Verificar documentos sem embeddings
- [ ] Verificar embeddings sem documentos
- [ ] Testar deleção em cascata
- [ ] Confirmar criação automática de embeddings
- [ ] Verificar tempos de sincronização

### Próximos Passos

1. Monitorar Tempos

```sql
-- Verificar delay entre criação de documento e embedding
SELECT
    d.id,
    d.created_at as doc_created,
    e.created_at as emb_created,
    e.created_at - d.created_at as delay
FROM documents d
JOIN embeddings e ON d.id = e.document_id
ORDER BY d.created_at DESC
LIMIT 5;
```

2. Verificar Integridade

```sql
-- Verificar se todos os documentos têm embeddings
SELECT COUNT(*) as docs_without_embeddings
FROM documents d
LEFT JOIN embeddings e ON d.id = e.document_id
WHERE e.id IS NULL;
```

3. Ações Corretivas (se necessário)

- [ ] Implementar trigger para deleç��o em cascata
- [ ] Adicionar verificação de integridade periódica
- [ ] Criar job para sincronização automática

## Teste de Contagem de Documentos

### 1. Verificar Valor Atual

```sql
-- Verificar contagem atual
SELECT * FROM statistics WHERE key = 'documents_count';
```

### 2. Testar Atualização Manual

```sql
-- Atualizar valor manualmente
UPDATE statistics
SET value = 5,
    updated_at = NOW()
WHERE key = 'documents_count';

-- Verificar se atualizou
SELECT * FROM statistics WHERE key = 'documents_count';
```

### 3. Testar Via API

```bash
# Adicionar documento para testar atualização automática
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "content": "Documento de teste para atualizar contagem",
    "metadata": {
      "title": "Teste Contagem",
      "document_hash": "teste_count_1"
    }
  }' \
  https://backend-rag-ia.onrender.com/api/v1/documents/

# Verificar via health check
curl https://backend-rag-ia.onrender.com/api/v1/health
```

### 4. Verificar Consistência

```sql
-- Comparar contagens
SELECT
    (SELECT COUNT(*) FROM documents) as real_count,
    (SELECT value FROM statistics WHERE key = 'documents_count') as stored_count,
    (SELECT COUNT(*) FROM documents) =
    (SELECT value FROM statistics WHERE key = 'documents_count') as is_consistent;
```

### 5. Função de Verificação

```sql
-- Criar função para verificar e corrigir contagem
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

-- Testar função
SELECT sync_documents_count();
SELECT * FROM statistics WHERE key = 'documents_count';
```

### Checklist de Testes

- [ ] Verificar valor inicial
- [ ] Testar atualização manual
- [ ] Confirmar atualização via API
- [ ] Verificar consistência
- [ ] Testar função de sincronização

### Próximos Passos

1. Monitorar Atualizações

```sql
-- Histórico de atualizações
SELECT
    value,
    updated_at,
    updated_at - LAG(updated_at) OVER (ORDER BY updated_at) as time_since_last_update
FROM statistics
WHERE key = 'documents_count'
ORDER BY updated_at DESC;
```

2. Verificar Triggers

```sql
-- Listar triggers relacionados
SELECT
    trigger_name,
    event_manipulation,
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE event_object_table IN ('documents', 'statistics')
ORDER BY trigger_name;
```
