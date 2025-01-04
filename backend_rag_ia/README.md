# CoFlow RAG API

API para gerenciamento de documentos e embeddings do sistema RAG.

## Funcionalidades

- Gerenciamento de documentos
- Geração e atualização de embeddings
- Monitoramento e estatísticas
- Operações em lote
- Logging de operações

## Tecnologias

- FastAPI
- Supabase
- Python 3.11+
- Docker
- PostgreSQL

## Configuração

1. Clone o repositório
2. Configure as variáveis de ambiente em um arquivo `.env`:

```bash
ENVIRONMENT=development
SUPABASE_URL=sua_url_do_supabase
SUPABASE_SERVICE_ROLE_KEY=sua_chave_de_servico
```

## Execução

### Com Docker

```bash
# Construir e iniciar containers
docker-compose up --build

# Executar em background
docker-compose up -d

# Parar containers
docker-compose down
```

### Sem Docker

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Execute a API:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

## Testes

### Executar todos os testes

```bash
pytest
```

### Executar testes específicos

```bash
# Testes unitários
pytest -m unit

# Testes de integração
pytest -m integration

# Testes de API
pytest -m api

# Testes de banco
pytest -m database
```

### Relatório de cobertura

```bash
# Gerar relatório
pytest --cov=app --cov-report=html

# Visualizar relatório
open htmlcov/index.html
```

## Documentação

- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`
- OpenAPI: `/api/openapi.json`

## Estrutura do Projeto

```
backend_rag_ia/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicação FastAPI
│   ├── config.py        # Configurações
│   └── schemas.py       # Schemas Pydantic
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Fixtures do pytest
│   └── test_api.py      # Testes da API
├── requirements.txt     # Dependências
├── pytest.ini          # Configuração do pytest
├── Dockerfile          # Configuração do Docker
├── docker-compose.yml  # Configuração do Docker Compose
└── README.md          # Documentação
```

## Endpoints

### Documentos

- `POST /api/v1/documents` - Criar documento
- `GET /api/v1/documents/{id}` - Buscar documento
- `PUT /api/v1/documents/{id}` - Atualizar documento
- `DELETE /api/v1/documents/{id}` - Remover documento

### Embeddings

- `POST /api/v1/embeddings` - Gerar embedding
- `POST /api/v1/documents/{id}/embedding` - Sincronizar embedding
- `GET /api/v1/documents/{id}/embedding/status` - Status do embedding
- `POST /api/v1/embeddings/sync` - Sincronizar embeddings faltantes

### Monitoramento

- `GET /api/v1/statistics` - Estatísticas atuais
- `GET /api/v1/statistics/history` - Histórico de estatísticas
- `GET /api/v1/health` - Status da API
- `GET /api/v1/logs` - Logs do sistema

### Operações em Lote

- `POST /api/v1/documents/batch` - Upload em lote
- `GET /api/v1/documents/batch/{id}` - Status da operação

## Desenvolvimento

### Convenções de Código

- Seguir PEP 8
- Usar type hints
- Documentar funções e classes
- Manter 100% de cobertura de testes

### Fluxo de Trabalho

1. Criar branch para feature
2. Implementar mudanças
3. Adicionar/atualizar testes
4. Verificar cobertura
5. Criar pull request

## Deploy

### Render

1. Conectar repositório
2. Configurar variáveis de ambiente
3. Selecionar branch principal
4. Configurar comando de build:

```bash
pip install -r requirements.txt
```

5. Configurar comando de start:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request

## Licença

Este projeto está sob a licença MIT.
