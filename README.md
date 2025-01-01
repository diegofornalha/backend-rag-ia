# backend-rag-ia

API para busca semântica e processamento de documentos usando FastAPI, Supabase+pgvector e Sentence Transformers.

## Características

- Busca semântica em documentos usando Supabase+pgvector
- Embeddings com Sentence Transformers
- Armazenamento de documentos e embeddings no Supabase
- API RESTful com FastAPI
- Containerização com Docker
- Deploy automatizado no Render

## Requisitos

- Python 3.11+
- pip
- virtualenv (opcional)
- Docker (obrigatório para deploy no Render)

## Instalação

1. Clone o repositório
2. Crie um ambiente virtual (opcional):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Executando em Desenvolvimento

Para iniciar o servidor de desenvolvimento:

```bash
uvicorn backend_rag_ia.api.main:app --reload --port 10000
```

A API estará disponível em:
http://127.0.0.1:10000

## Endpoints Principais

- `POST /api/v1/search`: Realiza busca semântica

  - Parâmetros:
    - `query`: Texto para buscar
    - `threshold` (opcional): Limiar de similaridade (0.0 a 1.0)
    - `limit` (opcional): Número máximo de resultados

- `GET /api/v1/documents`: Lista documentos
- `POST /api/v1/documents`: Adiciona um novo documento
- `GET /api/v1/documents/{doc_id}`: Obtém um documento
- `PUT /api/v1/documents/{doc_id}`: Atualiza um documento
- `DELETE /api/v1/documents/{doc_id}`: Remove um documento
- `GET /api/v1/statistics`: Obtém estatísticas do sistema
- `GET /api/v1/health`: Health check

## Variáveis de Ambiente Necessárias

- `SUPABASE_URL`: URL do projeto Supabase
- `SUPABASE_KEY`: Chave de API do Supabase
- `GEMINI_API_KEY`: Chave de API do Google Gemini
- `LANGCHAIN_CACHE_DIR`: Diretório para cache de embeddings (opcional)

## Desenvolvimento

1. Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

2. Execute os testes:

```bash
pytest
```

## Executando com Docker

1. Construa a imagem:

```bash
docker build -t rag-api .
```

2. Execute o container:

```bash
docker run -p 10000:10000 --env-file .env rag-api
```

## Deploy no Render

⚠️ **IMPORTANTE**: O deploy no Render **DEVE** ser feito usando Docker.

Para instruções detalhadas sobre como fazer o deploy no Render, consulte [Render.md](Render.md).
