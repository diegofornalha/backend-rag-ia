# Endpoints Necessários para Sistema RAG

## Documentos

### POST /api/v1/documents

- Criar novo documento
- Verifica duplicidade
- Retorna ID do documento

### PUT /api/v1/documents/{id}

- Atualizar documento existente
- Verifica necessidade de atualizar embedding

### GET /api/v1/documents/{id}

- Retorna documento e seu embedding

### DELETE /api/v1/documents/{id}

- Remove documento e seu embedding

## Embeddings

### POST /api/v1/embeddings

- Gera embedding para texto (já existente)
- Usado pelo processo de sincronização

### POST /api/v1/documents/{id}/embedding

- Gera/regenera embedding para documento específico

## Estatísticas

### GET /api/v1/statistics

- Retorna estatísticas atuais do sistema
- Contagens, métricas de processamento

### GET /api/v1/statistics/history

- Retorna histórico de estatísticas
- Permite análise de tendências

## Monitoramento

### GET /api/v1/health

- Status do sistema
- Métricas de performance

### GET /api/v1/logs

- Consulta logs do sistema
- Filtros por tipo, período, etc

## Batch Operations

### POST /api/v1/documents/batch

- Upload em lote de documentos
- Processamento assíncrono

### GET /api/v1/documents/batch/{batch_id}

- Status do processamento em lote
- Resultados parciais/finais

## Configuração Recomendada

1. **Infraestrutura**

   - Deploy no Render
   - Banco PostgreSQL com Supabase
   - Cache Redis para performance

2. **Segurança**

   - Autenticação via API key
   - Rate limiting
   - Logs de acesso

3. **Performance**
   - Processamento assíncrono para operações longas
   - Cache de resultados frequentes
   - Paginação em listagens
