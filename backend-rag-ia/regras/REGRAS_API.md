# Oracle API Documentation

## Estrutura do Projeto

```
backend/
├── api/
│   └── routes.py         # Rotas da API
├── models/
│   └── document.py       # Modelo de documento
├── services/
│   └── vector_store.py   # Serviço de gerenciamento de vetores e busca
└── utils/                # Utilitários
```

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
