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

## Executando localmente

```bash
chmod +x start.sh
./start.sh
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

## Endpoints

- `POST /api/v1/documents`: Adiciona um novo documento
- `POST /api/v1/search`: Realiza busca semântica
- `GET /api/v1/health`: Verifica o status da API
- `GET /health`: Health check da aplicação

## Variáveis de Ambiente

Veja `.env.example` para a lista completa de variáveis de ambiente necessárias.

## Desenvolvimento

1. Instale as dependências de desenvolvimento:

```bash
pip install -r requirements.txt
```

2. Execute os testes:

```bash
pytest
```
