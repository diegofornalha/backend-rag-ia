# Backend Local Rules

## Ambiente Local

- URL Base: `http://localhost:8000`
- Ambiente: Desenvolvimento
- Runtime: Python com venv
- Start Command: `python -m uvicorn main:app --reload`

## Configuração

### Arquivo .env.local

```env
ENVIRONMENT=local
MODEL_NAME=all-MiniLM-L6-v2
DEBUG=true

# Credenciais do Supabase (obrigatórias)
SUPABASE_URL=url_do_supabase
SUPABASE_KEY=chave_do_supabase
```

## Estrutura do Projeto

```
backend/               # Pasta raiz do backend
├── clusters/
│   └── supabase/
│       ├── api/
│       ├── models/
│       ├── services/
│       ├── documents/
│       ├── scripts/
│       └── sql/
├── config/
├── deploy/
├── debug/
├── docs/
├── tools/
└── indexes/
```

## Regras de Desenvolvimento

1. **Ambiente Virtual**

   - Usar `venv` para isolamento
   - Manter `requirements.txt` atualizado
   - Ativar com `source venv/bin/activate`

2. **Configurações**

   - Usar `.env.local` para desenvolvimento
   - Nunca commitar arquivos `.env`
   - Manter `.env.example` atualizado

3. **Código**

   - Seguir PEP 8
   - Usar tipagem estática
   - Documentar funções e classes
   - Manter testes atualizados

4. **Logs**
   - Usar o logger configurado
   - Níveis: DEBUG, INFO, WARNING, ERROR
   - Formato: timestamp - módulo - nível - mensagem

## Endpoints

Os mesmos endpoints do ambiente Render, mas localmente:

### Health Check

```http
GET http://localhost:8000/api/v1/health
```

### Adicionar Documento

```http
POST http://localhost:8000/api/v1/documents/
```

### Buscar Documentos

```http
POST http://localhost:8000/api/v1/search/
```

### Verificar Documento

```http
GET http://localhost:8000/api/v1/documents/check/{document_hash}
```

### Contar Documentos

```http
GET http://localhost:8000/api/v1/documents/count
```

### Deletar Documento

```http
DELETE http://localhost:8000/api/v1/documents/{doc_id}
```

## Debug e Desenvolvimento

1. **Logs em Tempo Real**

   ```bash
   python -m uvicorn main:app --reload --log-level debug
   ```

2. **Testes Locais**

   ```bash
   pytest tests/
   ```

3. **Verificação de Tipos**

   ```bash
   mypy .
   ```

4. **Formatação**
   ```bash
   black .
   flake8 .
   ```

## Monitoramento Local

- **Logs**: Terminal/Console
- **API Docs**: `http://localhost:8000/docs`
- **OpenAPI**: `http://localhost:8000/openapi.json`
- **Status**: `http://localhost:8000/api/v1/health`
- **Debug**: `http://localhost:8000/api/v1/debug`

## Troubleshooting

1. **Porta em Uso**

   ```bash
   lsof -i :8000
   kill -9 PID
   ```

2. **Problemas de Dependências**

   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

3. **Erro de Conexão Supabase**
   - Verificar `.env.local`
   - Testar conexão com `curl`
   - Verificar logs do Supabase
