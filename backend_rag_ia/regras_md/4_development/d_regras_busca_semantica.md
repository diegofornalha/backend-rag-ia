# Regras de Busca Semântica (RAG)

> ⚠️ Este documento define as regras do sistema RAG (Retrieval Augmented Generation).
> O sistema integra busca semântica, armazenamento vetorial e processamento LLM.

## 1. Visão Geral

- **Objetivo**: Sistema RAG eficiente e resiliente
- **Modelo Base**: `all-MiniLM-L6-v2` para embeddings
- **Stack Principal**:
  - Python 3.11
  - Supabase + pgvector (armazenamento vetorial)
  - Google Gemini (processamento LLM)
  - FastAPI (endpoints RESTful)

## 2. Componentes RAG

1. **Retrieval (Recuperação)**:

   - Embeddings via Sentence Transformers
   - Armazenamento vetorial no Supabase/pgvector
   - Busca por similaridade cosine
   - Fallback para busca textual

2. **Augmentation (Enriquecimento)**:

   - Reranking de resultados
   - Metadados e contexto
   - Filtros e pesos customizados
   - Cache em múltiplas camadas

3. **Generation (Geração)**:
   - Processamento LLM dos resultados
   - Respostas contextualizadas
   - Explicações em linguagem natural
   - Formatação rica de saída

## 3. Regras de Implementação

1. **Busca Semântica**:

   - Usar Sentence Transformers para embeddings
   - Armazenar vetores no pgvector
   - Implementar threshold configurável
   - Otimizar índices vetoriais

2. **Estratégias de Fallback**:

   - Busca textual como backup
   - Filtros por metadados
   - Full-text search
   - Logging detalhado de falhas

3. **Integração LLM**:

   - Processamento assíncrono
   - Retry com backoff
   - Cache de respostas
   - Tratamento de erros

4. **API e Endpoints**:
   - RESTful bem definido
   - Validação robusta
   - Documentação OpenAPI
   - Versionamento adequado

## 4. Arquitetura e Integração

1. **Estrutura de Serviços**:

   - `SemanticSearchManager`: Orquestra o fluxo RAG
   - `LLMManager`: Processa com Gemini/outros LLMs
   - `VectorStore`: Gerencia embeddings e cache

2. **⚠️ Regras de Integração CLI-Serviços**:

   - CLI DEVE usar os mesmos serviços da API
   - PROIBIDO implementações paralelas/distintas
   - Reutilizar `SemanticSearchManager` para busca
   - Manter consistência entre CLI e API

3. **Fluxo de Dados RAG**:

   ```
   Query → Embedding → Busca Vetorial → Reranking → LLM → Resposta
           ↓            ↓               ↓           ↓
        Cache       pgvector      Filtros    Processamento
   ```

4. **Responsabilidades**:

   - CLI: Interface e formatação
   - Serviços: Lógica RAG
   - API: Endpoints e validação
   - Banco: Vetores e matching

5. **Boas Práticas**:
   - Centralizar lógica RAG nos serviços
   - CLI/API como interfaces
   - Cache em múltiplas camadas
   - Monitoramento e métricas

## 5. Manutenção e Evolução

1. **Monitoramento**:

   - Latência de busca
   - Hit rate de cache
   - Qualidade das respostas
   - Uso de recursos

2. **Otimizações**:

   - Índices vetoriais
   - Estratégias de cache
   - Batch processing
   - Compressão de embeddings

3. **Documentação**:
   - Atualizar fluxos
   - Documentar problemas
   - Manter exemplos
   - Registrar decisões
