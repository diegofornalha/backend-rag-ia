# Regras do Projeto Backend RAG

## 1. Estrutura do Projeto

### 1.1 Organização de Pastas

```
backend-rag-ai/
├── 1_core/              # Núcleo do projeto
│   ├── config/          # Configurações
│   └── rules/           # Regras e documentação
├── 2_database/          # Banco de dados
│   ├── migrations/      # Migrações
│   └── schemas/         # Esquemas
├── 3_deployment/        # Deploy
│   ├── docker/          # Configurações Docker
│   └── scripts/         # Scripts de deploy
└── 4_development/       # Desenvolvimento
    ├── docs/            # Documentação
    └── tests/           # Testes
```

### 1.2 Regras de Organização

1. **Arquivos**:

   - ❌ NUNCA deixar arquivos soltos na raiz
   - ✅ SEMPRE organizar em subpastas apropriadas
   - ✅ Usar nomes descritivos e significativos

2. **Pastas**:
   - ✅ Seguir numeração consistente
   - ✅ Usar prefixos padronizados
   - ✅ Manter hierarquia clara

## 2. Padrões de Código

### 2.1 Python

1. **Estilo**:

   - Seguir PEP 8
   - Usar `snake_case` para funções e variáveis
   - Usar `PascalCase` para classes
   - Usar `UPPER_CASE` para constantes

2. **Documentação**:
   - Docstrings em todas as funções/classes
   - Type hints em todos os parâmetros
   - Exemplos de uso quando relevante

### 2.2 SQL

1. **Nomenclatura**:

   - Tabelas: plural, `snake_case`
   - Colunas: singular, `snake_case`
   - Índices: `idx_tabela_coluna`

2. **Queries**:
   - Keywords em UPPERCASE
   - Uma cláusula por linha
   - Indentação consistente

## 3. Configurações

### 3.1 Ambiente

1. **Python**:

   - Versão: 3.11
   - Virtual env obrigatório
   - Requirements.txt atualizado

2. **Cache**:
   - Redis como backend
   - Limpeza automática
   - Métricas habilitadas

### 3.2 Banco de Dados

1. **PostgreSQL**:
   - pgvector habilitado
   - Índices otimizados
   - Pool configurado

## 4. Desenvolvimento

### 4.1 Fluxo de Trabalho

1. **Branches**:

   - `feature/*`: novas funcionalidades
   - `fix/*`: correções
   - `docs/*`: documentação
   - `refactor/*`: refatoração

2. **Commits**:
   - Mensagens descritivas
   - Prefixos padronizados
   - Referência ao embate

### 4.2 Testes

1. **Unitários**:

   - Cobertura mínima: 80%
   - Fixtures padronizadas
   - Nomes descritivos

2. **Integração**:
   - Ambiente isolado
   - Dados de teste limpos
   - Timeouts definidos

## 5. Segurança

### 5.1 Dados

1. **Sensíveis**:

   - Nunca em código
   - Sempre em .env
   - Rotação regular

2. **Acessos**:
   - CORS configurado
   - Rate limiting
   - Autenticação obrigatória

### 5.2 Deployment

1. **Containers**:

   - Imagens mínimas
   - Usuário não-root
   - Scan de vulnerabilidades

2. **Monitoramento**:
   - Logs centralizados
   - Métricas exportadas
   - Alertas configurados

## 6. Manutenção

### 6.1 Logs

1. **Formato**:

   - Timestamp ISO 8601
   - Nível de log apropriado
   - Contexto suficiente

2. **Retenção**:
   - Rotação diária
   - Compressão automática
   - Backup semanal

### 6.2 Performance

1. **Otimizações**:

   - Cache estratégico
   - Queries otimizadas
   - Assets comprimidos

2. **Monitoramento**:
   - APM habilitado
   - Métricas de uso
   - Dashboards atualizados
