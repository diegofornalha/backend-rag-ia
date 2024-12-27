# Oráculo API

API de busca semântica e processamento de documentos usando FastAPI, Supabase e LangChain.

## Requisitos

- Docker
- Python 3.12+
- Supabase Account
- Google Cloud (para Gemini API)
- Render Account

## Variáveis de Ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```env
# Configurações do Servidor
PORT=8000
HOST=0.0.0.0
ENV=prod
PYTHON_VERSION=3.12.0

# API Keys e Tokens
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_token
RENDER_DEPLOY_HOOK=your_render_deploy_hook

# LangChain
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=your_project_name
LANGCHAIN_CACHE_DIR=/app/cache/langchain

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Outras Configurações
LOG_LEVEL=INFO
WORKERS=4
DEBUG=False

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

## Usando a Imagem Docker

### Pull da Imagem

```bash
docker pull ghcr.io/diegofornalha/backend-rag-ia:latest
```

### Executando o Container

```bash
docker run -d -p 8000:8000 --env-file .env --name backend ghcr.io/diegofornalha/backend-rag-ia:latest
```

### Verificando o Status

```bash
curl http://localhost:8000/api/v1/health
```

## Desenvolvimento Local

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv venv`
3. Ative o ambiente virtual: `source venv/bin/activate` (Linux/Mac) ou `venv\Scripts\activate` (Windows)
4. Instale as dependências: `pip install -r requirements.txt`
5. Configure as variáveis de ambiente no arquivo `.env`
6. Execute o servidor: `uvicorn oracle:app --reload`

## Endpoints da API

- `GET /api/v1/health`: Verifica a saúde da aplicação
- `POST /api/v1/documents/`: Adiciona um documento
- `POST /api/v1/search/`: Realiza busca por similaridade
- `DELETE /api/v1/documents/{doc_id}`: Remove um documento

## CI/CD

O projeto usa GitHub Actions para:

1. Construir a imagem Docker
2. Publicar a imagem no GitHub Container Registry
3. Fazer deploy automático no Render

## Processo de Deploy e Alterações

### ⚠️ Ordem Importante de Alterações

Para evitar problemas ao fazer alterações no projeto, sempre siga esta ordem:

1. Fazer as alterações no código
2. Commitar e fazer push para o GitHub
3. **Aguardar o deploy completo no Render**
   - Esperar o build terminar
   - Aguardar o serviço reiniciar
   - Confirmar que está rodando com as novas alterações
4. Só então testar as novas funcionalidades

Se os testes forem feitos antes do deploy terminar, você pode encontrar erros porque:

- O código antigo ainda está rodando
- Novos endpoints podem não estar disponíveis
- Alterações no banco de dados podem não estar sincronizadas

### 🔄 Tempo de Deploy

- O deploy no Render pode levar alguns minutos
- Em planos gratuitos, o cold start inicial pode demorar mais
- Aguarde a confirmação de "Deploy Success" antes de prosseguir

## Licença

MIT
