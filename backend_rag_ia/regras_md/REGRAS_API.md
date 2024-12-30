# Regras da API

## Princípios de Harmonia e Coerência

> **Regra Fundamental**: Todo o sistema deve manter perfeita ordem e harmonia, garantindo que cada componente se comunique adequadamente dentro de seu contexto.

### 1. Coerência Contextual

- Cada endpoint deve ter um propósito claro e bem definido
- Metadados devem ser consistentes com o contexto do documento
- Embeddings devem refletir precisamente o conteúdo semântico
- Respostas da API devem ser coerentes com as requisições

### 2. Harmonia entre Componentes

- Documentos ↔️ Embeddings: Sincronização perfeita
- Metadados ↔️ Conteúdo: Alinhamento semântico
- Buscas ↔️ Resultados: Relevância contextual
- Requisições ↔️ Respostas: Consistência lógica

### 3. Integridade Relacional

- Manter vínculos corretos entre documentos e embeddings
- Garantir consistência entre metadados globais e específicos
- Preservar relações entre documentos similares
- Assegurar rastreabilidade das operações

### 4. Avisos e Feedbacks Obrigatórios

#### Avisos Recorrentes que Requerem Autorização

- **Alterações Críticas**:

  - Modificações em endpoints existentes
  - Atualizações de schema do banco
  - Alterações nas regras de embedding
  - Mudanças nos parâmetros de busca

- **Problemas de Performance**:

  - Alto consumo de memória durante sincronização
  - Lentidão nas respostas dos endpoints
  - Falhas recorrentes na geração de embeddings
  - Degradação no tempo de resposta das buscas

- **Questões de Integridade**:
  - Documentos sem embeddings por mais de 24h
  - Inconsistências entre documentos e embeddings
  - Falhas na deduplicação automática
  - Erros de sincronização persistentes

#### Solicitação de Feedback

- **Quando Solicitar**:

  - Resultados inesperados nas buscas semânticas
  - Comportamento anômalo na deduplicação
  - Falhas não previstas na documentação
  - Divergências entre comportamento esperado e real

- **Como Reportar**:

  - Descrever o problema detalhadamente
  - Fornecer logs relevantes
  - Sugerir possíveis soluções
  - Indicar impacto no sistema

- **Acompanhamento**:
  - Registrar decisões tomadas
  - Documentar soluções aplicadas
  - Monitorar efetividade das correções
  - Atualizar documentação quando necessário

## Auto-Aprendizado e Melhorias

### 1. Registro de Otimizações

- **Sincronização e Deduplicação**:

  - Implementado sistema inteligente de hash para detecção de duplicatas
  - Remoção automática mantendo documentos originais
  - Preservação de embeddings dos documentos principais
  - Limpeza cascata de embeddings órfãos

- **Monitoramento de Eficiência**:
  - Rastreamento de tempo de processamento
  - Contagem de documentos antes/depois
  - Taxa de sucesso nas operações
  - Métricas de performance

### 2. Histórico de Melhorias

- **Última Atualização**: 29/12/2023
  - Implementada sincronização inteligente de documentos
  - Adicionada detecção de conteúdo duplicado
  - Otimizado processo de remoção em cascata
  - Melhorada visualização de estatísticas

### 3. Processo de Evolução

- **Identificação de Padrões**:

  - Análise de problemas recorrentes
  - Detecção de gargalos de performance
  - Avaliação de feedback dos usuários
  - Monitoramento de falhas

- **Implementação de Soluções**:
  - Desenvolvimento de correções
  - Testes de eficácia
  - Documentação das mudanças
  - Atualização das regras

### 4. Ciclo de Melhoria Contínua

1. **Observar**: Monitorar comportamento do sistema
2. **Analisar**: Identificar pontos de melhoria
3. **Planejar**: Desenvolver soluções
4. **Implementar**: Aplicar melhorias
5. **Documentar**: Atualizar regras e documentação
6. **Verificar**: Validar eficácia das mudanças

## Observações Importantes

> **Nota sobre Notificações**: Este projeto atualmente é mantido individualmente, sem necessidade de notificações de equipe. Caso futuramente seja expandido para uma equipe, implementar sistema de notificações para:
>
> - Alterações em endpoints críticos
> - Atualizações de documentação
> - Mudanças em regras de negócio
> - Alterações de schema

## Endpoints

### POST /api/v1/documents/

Adiciona novos documentos ao índice.

**Request:**

```json
{
  "documents": [
    {
      "content": "Texto do documento",
      "metadata": {
        "type": "profile",
        "tags": ["biografia", "profissional"]
      }
    }
  ]
}
```

**Response:**

```json
{
  "message": "Processando 1 documentos em background"
}
```

### DELETE /api/v1/documents/{document_id}

Remove um documento específico e seu embedding.

**Response:**

```json
{
  "message": "Documento removido com sucesso",
  "document_id": "123"
}
```

### PUT /api/v1/documents/{document_id}

Atualiza um documento existente.

**Request:**

```json
{
  "content": "Novo texto do documento",
  "metadata": {
    "type": "profile",
    "tags": ["biografia", "profissional"]
  }
}
```

**Response:**

```json
{
  "message": "Documento atualizado com sucesso",
  "document_id": "123"
}
```

### POST /api/v1/search/

Realiza busca semântica nos documentos.

**Request:**

```json
{
  "query": "string",
  "k": 4,
  "filters": {
    "type": "profile",
    "tecnologias": ["Python"],
    "content_types": ["biografia"]
  }
}
```

**Response:**

```json
[
  {
    "content": "Texto encontrado",
    "metadata": {
      "type": "profile",
      "timestamp": "2024-03-21T10:30:00",
      "pessoas": ["Diego Fornalha"],
      "tecnologias": ["Python"],
      "content_types": ["biografia"]
    },
    "embedding_id": 1
  }
]
```

### GET /api/v1/documents/{document_id}

Retorna um documento específico por ID.

**Response:**

```json
{
  "id": "123",
  "content": "Texto do documento",
  "metadata": {
    "type": "profile",
    "tags": ["biografia", "profissional"]
  },
  "embedding_id": 1,
  "created_at": "2024-03-21T10:30:00"
}
```

### GET /api/v1/health

Verifica o status da API.

**Response:**

```json
{
  "status": "healthy",
  "message": "API está funcionando normalmente",
  "documents_count": 3
}
```

### GET /api/v1/documents/count

Retorna o número total de documentos armazenados.

**Response:**

```json
{
  "count": 3
}
```

### POST /api/v1/embeddings/sync

Sincroniza embeddings para documentos que não os possuem.

**Response:**

```json
{
  "message": "Sincronização iniciada",
  "documents_to_process": 5
}
```

### GET /api/v1/embeddings/status

Verifica o status da sincronização de embeddings.

**Response:**

```json
{
  "total_documents": 10,
  "documents_with_embeddings": 8,
  "documents_without_embeddings": 2,
  "last_sync": "2024-03-21T10:30:00"
}
```

## Funcionalidades

### Deduplicação Inteligente

- Threshold de similaridade: 0.8
- Análise de conteúdo para evitar redundância
- Consolidação de informações similares

### Processamento de Metadados

- Extração automática de entidades
- Categorização de conteúdo
- Normalização de nomes e termos
- Indexação otimizada para busca rápida

### Busca Avançada

- Busca semântica com FAISS
- Filtragem por metadados
- Combinação de múltiplos critérios
- Ordenação por relevância

### Exemplo de Uso

```python
# Busca por tipo específico
docs = vector_store.filter_by_metadata({
    "content_types": "tutorial"
})

# Busca combinada
docs = vector_store.filter_by_metadata({
    "pessoas": "Diego Fornalha",
    "tecnologias": "Python",
    "content_types": "projeto"
})
```

## Notas de Implementação

1. **Indexação**:

   - Uso de FAISS para busca semântica
   - Índice invertido para metadados
   - Batch processing para melhor performance

2. **Otimizações**:

   - Processamento em background
   - Deduplicação automática
   - Caching de embeddings
   - Normalização de entidades

3. **Persistência**:

   - Salvamento automático de índices
   - Backup de metadados
   - Formato JSON otimizado

4. **Segurança**:
   - Validação de entrada
   - Sanitização de dados
   - Logging de operações
