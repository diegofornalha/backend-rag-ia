# Upload de Documentos para o Supabase

## 1. Estrutura do Processo

### 1.1 Fluxo de Upload

1. **Leitura dos Arquivos**:

   - Leitura recursiva de arquivos markdown
   - Extração de metadados (título, caminho, tamanho)
   - Cálculo de hashes para controle de versão

2. **Preparação dos Dados**:

   - Normalização do conteúdo
   - Geração de identificadores únicos
   - Estruturação dos metadados

3. **Upload para Supabase**:
   - Inserção na tabela principal (`rag.01`)
   - Geração de embeddings via API
   - Armazenamento de embeddings (`rag.02_embeddings_regras_geral`)

### 1.2 Campos Obrigatórios

1. **Documento Principal** (`rag.01`):

   - `version_key`: Identificador único do documento
   - `titulo`: Título extraído do arquivo
   - `conteudo`: Objeto com texto e metadados
   - `error_log`: Registro de erros (se houver)
   - `created_at`: Data de criação
   - `updated_at`: Data de atualização
   - `processing_status`: Status do processamento
   - `content_hash`: Hash do conteúdo
   - `document_hash`: Hash do documento
   - `metadata`: Metadados adicionais

2. **Embeddings** (`rag.02_embeddings_regras_geral`):
   - `document_id`: Referência ao documento original
   - `embedding`: Vetor de embedding
   - `content_hash`: Hash do conteúdo
   - `processing_status`: Status do processamento
   - `last_embedding_update`: Data da última atualização

## 2. Implementação

### 2.1 Configuração

```python
# Carregar variáveis de ambiente
load_dotenv()

# Configurar cliente Supabase
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)
```

### 2.2 Processamento de Documentos

```python
# Ler arquivos markdown
documents = read_markdown_files('01_regras_md_apenas_raiz')

# Para cada documento
for doc in documents:
    # Preparar dados
    document_data = {
        'version_key': doc['version_key'],
        'titulo': doc['titulo'],
        'conteudo': doc['conteudo'],
        'content_hash': calculate_hash(content),
        'document_hash': calculate_hash(path),
        'metadata': {
            'file_path': path,
            'file_name': name,
            'file_size': size
        }
    }

    # Inserir no Supabase
    result = supabase.table('rag.01').insert(document_data).execute()
```

### 2.3 Geração de Embeddings

```python
# Gerar embedding via API
embedding = await generate_embedding(doc['conteudo']['text'])

# Inserir embedding
if embedding:
    embedding_data = {
        'document_id': document_id,
        'embedding': embedding,
        'content_hash': doc['content_hash'],
        'processing_status': 'completed',
        'last_embedding_update': current_time
    }

    supabase.table('rag.02_embeddings_regras_geral').insert(embedding_data).execute()
```

## 3. Boas Práticas

### 3.1 Validação

- Verificar existência de documentos duplicados
- Validar integridade dos dados
- Confirmar geração de embeddings
- Monitorar status de processamento

### 3.2 Tratamento de Erros

- Registrar erros detalhadamente
- Implementar retry para falhas temporárias
- Manter status de processamento atualizado
- Permitir reprocessamento quando necessário

### 3.3 Performance

- Processar documentos em lotes
- Implementar delays entre requisições
- Monitorar uso de recursos
- Otimizar tamanho dos lotes

## 4. Monitoramento

### 4.1 Métricas

- Total de documentos processados
- Taxa de sucesso/falha
- Tempo médio de processamento
- Uso de recursos

### 4.2 Logs

- Nível de log adequado
- Informações relevantes
- Rastreamento de erros
- Métricas de performance

## 5. Troubleshooting

### 5.1 Problemas Comuns

1. **Erro de Conexão**:

   - Verificar credenciais
   - Confirmar URL do Supabase
   - Validar permissões

2. **Falha no Embedding**:

   - Verificar disponibilidade da API
   - Validar formato dos dados
   - Confirmar limites de tamanho

3. **Duplicatas**:
   - Verificar hashes
   - Validar chaves únicas
   - Confirmar regras de negócio

### 5.2 Soluções

1. **Validação de Ambiente**:

   - Confirmar variáveis de ambiente
   - Testar conexões
   - Verificar permissões

2. **Reprocessamento**:

   - Identificar documentos com erro
   - Corrigir problemas específicos
   - Reprocessar seletivamente

3. **Otimização**:
   - Ajustar tamanho dos lotes
   - Configurar timeouts
   - Implementar retries

## 6. Geração de Embeddings

### 6.1 Integração com API

```python
# Configuração do cliente HTTP
async def generate_embedding(text: str) -> List[float]:
    url = 'https://api.coflow.com.br/api/v1/embeddings'
    headers = {'Content-Type': 'application/json'}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={'text': text},
            headers=headers,
            timeout=30.0
        )
        return response.json()['embedding']
```

### 6.2 Processo Assíncrono

- Processamento em background
- Retry automático em caso de falhas
- Limite de requisições por minuto
- Monitoramento de status

### 6.3 Atualização de Embeddings

- Verificação periódica de documentos sem embedding
- Reprocessamento em caso de falha
- Atualização de embeddings desatualizados
- Log de tentativas e resultados

## 7. Segurança e Permissões

### 7.1 Políticas de Acesso

- Uso do `service_role` para operações de escrita
- Políticas RLS para leitura
- Controle granular de permissões
- Auditoria de acessos

### 7.2 Credenciais

- Armazenamento seguro em variáveis de ambiente
- Rotação periódica de chaves
- Monitoramento de uso
- Logs de acesso

## 8. Versionamento

### 8.1 Controle de Versão

- Hash do conteúdo para identificar mudanças
- Versionamento semântico dos documentos
- Histórico de alterações
- Rastreamento de atualizações

### 8.2 Processo de Atualização

```python
async def update_document(doc_id: str, new_content: dict):
    # Calcular novo hash
    new_hash = calculate_hash(new_content)

    # Verificar se houve mudança
    if new_hash != current_hash:
        # Atualizar documento
        supabase.table('rag.01').update({
            'conteudo': new_content,
            'content_hash': new_hash,
            'updated_at': datetime.now(),
            'version_key': generate_version_key()
        }).eq('id', doc_id).execute()

        # Gerar novo embedding
        new_embedding = await generate_embedding(new_content['text'])
        if new_embedding:
            update_embedding(doc_id, new_embedding)
```

### 8.3 Histórico

- Registro de todas as versões
- Possibilidade de rollback
- Comparação entre versões
- Métricas de alterações

## 9. Backup e Recuperação

### 9.1 Estratégia de Backup

```python
async def backup_documents():
    # Exportar documentos
    documents = supabase.table('rag.01').select('*').execute()

    # Exportar embeddings
    embeddings = supabase.table('rag.02_embeddings_regras_geral').select('*').execute()

    # Salvar em formato estruturado
    backup_data = {
        'timestamp': datetime.now().isoformat(),
        'documents': documents.data,
        'embeddings': embeddings.data
    }

    # Salvar backup
    with open(f'backup_{datetime.now():%Y%m%d}.json', 'w') as f:
        json.dump(backup_data, f, indent=2)
```

### 9.2 Processo de Recuperação

- Restauração completa ou seletiva
- Validação de integridade
- Reconstrução de índices
- Verificação de consistência

### 9.3 Retenção de Backups

- Política de retenção
- Rotação automática
- Compressão de dados
- Validação periódica

## 10. Integração com Sistemas Externos

### 10.1 APIs Disponíveis

1. **Geração de Embeddings**:

```python
POST https://api.coflow.com.br/api/v1/embeddings
Content-Type: application/json

{
    "text": "conteúdo do documento"
}
```

2. **Consulta de Documentos**:

```python
POST https://api.coflow.com.br/api/v1/documents/search
Content-Type: application/json

{
    "query": "termo de busca",
    "limit": 10
}
```

### 10.2 Webhooks

- Notificações de atualização
- Callbacks de processamento
- Eventos de sistema
- Monitoramento de status

### 10.3 Rate Limiting

- Limites por endpoint
- Janelas de tempo
- Retry strategies
- Circuit breakers

## 11. Testes e Validação

### 11.1 Testes Unitários

```python
import pytest
from unittest.mock import Mock, patch

def test_document_upload():
    # Mock do cliente Supabase
    mock_supabase = Mock()
    mock_supabase.table().insert().execute.return_value = {'data': [{'id': '123'}]}

    # Teste de upload
    with patch('supabase.create_client', return_value=mock_supabase):
        result = upload_document({
            'titulo': 'Test Doc',
            'conteudo': {'text': 'test content'},
            'version_key': 'test-v1'
        })
        assert result['id'] == '123'
```

### 11.2 Testes de Integração

1. **Pipeline Completo**:

   - Upload de documento
   - Geração de embedding
   - Verificação de consistência
   - Validação de índices

2. **Cenários de Erro**:
   - Falha de conexão
   - Timeout na API
   - Dados inválidos
   - Conflitos de versão

### 11.3 Validação de Performance

1. **Métricas Chave**:

   - Tempo de upload
   - Latência de embedding
   - Uso de memória
   - Throughput

2. **Testes de Carga**:
   - Upload em massa
   - Concorrência
   - Limites do sistema
   - Recuperação de falhas

### 11.4 Checklist de Validação

1. **Pré-Produção**:

   - [ ] Testes unitários passando
   - [ ] Testes de integração OK
   - [ ] Métricas dentro do esperado
   - [ ] Logs configurados
   - [ ] Backups testados
   - [ ] Permissões verificadas

2. **Monitoramento Contínuo**:
   - [ ] Alertas configurados
   - [ ] Dashboards ativos
   - [ ] Rate limits ajustados
   - [ ] Rotação de logs
   - [ ] Backup automático
   - [ ] Verificação de integridade

## 12. Governança e Compliance

### 12.1 Políticas de Dados

1. **Retenção de Dados**:

   - Período de retenção definido
   - Processo de expurgo automático
   - Arquivamento de dados históricos
   - Documentação de políticas

2. **Classificação de Informações**:
   - Níveis de sensibilidade
   - Requisitos de proteção
   - Controles de acesso
   - Auditoria de uso

### 12.2 Auditoria

```python
async def audit_document_access(
    document_id: str,
    user_id: str,
    action: str,
    metadata: dict
):
    audit_entry = {
        'document_id': document_id,
        'user_id': user_id,
        'action': action,
        'timestamp': datetime.now().isoformat(),
        'metadata': metadata
    }

    await supabase.table('rag.03_audit_log').insert(audit_entry).execute()
```

### 12.3 Conformidade

1. **Requisitos Legais**:

   - LGPD/GDPR quando aplicável
   - Proteção de dados sensíveis
   - Direitos dos titulares
   - Processos de conformidade

2. **Documentação**:
   - Políticas e procedimentos
   - Registros de alterações
   - Trilhas de auditoria
   - Relatórios de compliance

### 12.4 Monitoramento de Compliance

1. **Verificações Periódicas**:

   - [ ] Revisão de permissões
   - [ ] Auditoria de acessos
   - [ ] Validação de políticas
   - [ ] Testes de conformidade

2. **Relatórios**:
   - Métricas de compliance
   - Violações identificadas
   - Ações corretivas
   - Recomendações

## 13. Resolução de Problemas em Produção

### 13.1 Diagnóstico Rápido

1. **Verificações Iniciais**:

   ```bash
   # Verificar status do serviço
   curl -I https://api.coflow.com.br/health

   # Verificar últimos logs
   tail -f logs/application.log | grep ERROR

   # Verificar métricas básicas
   SELECT COUNT(*) as total,
          COUNT(*) FILTER (WHERE error_log IS NOT NULL) as errors,
          MAX(updated_at) as last_update
   FROM rag.01;
   ```

### 13.2 Problemas Comuns e Soluções

1. **Falha na Geração de Embeddings**:

   ```python
   # Verificar status de embeddings pendentes
   async def check_pending_embeddings():
       result = await supabase.table('rag.01')\
           .select('id', 'titulo')\
           .is_('embedding', 'null')\
           .execute()

       for doc in result.data:
           print(f"Documento pendente: {doc['id']} - {doc['titulo']}")
   ```

2. **Inconsistência de Dados**:

   ```sql
   -- Verificar documentos sem hash
   SELECT id, titulo
   FROM rag.01
   WHERE content_hash IS NULL;

   -- Verificar embeddings órfãos
   SELECT e.document_id
   FROM rag.02_embeddings_regras_geral e
   LEFT JOIN rag.01 d ON e.document_id = d.id
   WHERE d.id IS NULL;
   ```

### 13.3 Procedimentos de Recuperação

1. **Reprocessamento de Documentos**:

   ```python
   async def reprocess_failed_documents():
       # Identificar documentos com erro
       failed = await supabase.table('rag.01')\
           .select('id', 'conteudo')\
           .not_.is_('error_log', 'null')\
           .execute()

       for doc in failed.data:
           try:
               # Limpar erro e tentar novamente
               await process_document(doc['id'], doc['conteudo'])
               print(f"Reprocessado com sucesso: {doc['id']}")
           except Exception as e:
               print(f"Falha no reprocessamento: {doc['id']} - {str(e)}")
   ```

2. **Reconstrução de Índices**:
   ```sql
   -- Reconstruir índices se necessário
   REINDEX TABLE rag.01;
   REINDEX TABLE rag.02_embeddings_regras_geral;
   ```

### 13.4 Prevenção de Problemas

1. **Monitoramento Proativo**:

   - Alertas de threshold
   - Métricas de saúde
   - Tendências de erro
   - Capacidade do sistema

2. **Manutenção Preventiva**:

   - Limpeza de logs antigos
   - Otimização de índices
   - Validação de backups
   - Testes de recuperação

3. **Documentação de Incidentes**:
   - Registro detalhado
   - Análise de causa raiz
   - Ações corretivas
   - Lições aprendidas
