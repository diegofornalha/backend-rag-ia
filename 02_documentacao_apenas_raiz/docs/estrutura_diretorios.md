# Estrutura de Diretórios do Projeto

## Visão Geral

O projeto está organizado em duas categorias principais:

1. Core do Backend (backend_rag_ia)
2. Diretórios Auxiliares (com prefixos numéricos por prioridade)

## Core do Backend (backend_rag_ia/)

Contém toda a lógica de negócio e regras principais do sistema:

```
backend_rag_ia/
├── __pycache__/    # Cache do Python
├── api/            # Endpoints e rotas da API
├── cli/            # Interface de linha de comando
├── config/         # Configurações do projeto
├── dados/          # Gerenciamento de dados
├── debugger/       # Ferramentas de debug
├── models/         # Modelos de dados/entidades
├── services/       # Serviços e lógica de negócio
└── utils/          # Utilitários e helpers
```

## Diretórios Auxiliares

### 00_testes_apenas_raiz/

Prioridade máxima - Testes e qualidade do código

```
├── core/          # Testes do core
├── unit/          # Testes unitários gerais
└── integration/   # Testes de integração gerais
```

### 01_regras_md_apenas_raiz/

Regras de negócio em formato markdown

```
└── docs/          # Documentação das regras
```

### 02_documentacao_apenas_raiz/

Documentação do projeto

```
├── docs/          # Documentação geral
└── schemas/       # Schemas e definições
```

### 03_ferramentas_rag_apenas_raiz/

Ferramentas específicas para RAG

```
└── cli/           # Ferramentas de linha de comando
```

### 04_dados_apenas_raiz/

Dados e recursos do projeto

```
├── fixtures/      # Dados de teste
└── embates/       # Registros de embates e decisões
```

### 05_sql_apenas_raiz/

Scripts e migrações SQL

```
├── migrations/    # Migrações do banco
└── queries/       # Queries úteis
```

### 06_scripts_apenas_raiz/

Scripts utilitários

```
└── utils/         # Scripts diversos
```

### 07_monitoring_apenas_raiz/

Monitoramento e observabilidade

```
├── core/          # Monitoramento do core
└── external/      # Monitoramento de sistemas externos
```

## Regras de Organização

1. O core do backend (backend_rag_ia/) mantém a estrutura tradicional de um projeto Python
2. Todos os outros diretórios seguem o padrão XX_nome_apenas_raiz onde:
   - XX é um número único que indica prioridade (00-99)
   - nome descreve o propósito do diretório
   - \_apenas_raiz indica que o diretório só pode existir na raiz
3. Quanto menor o número, maior a prioridade do diretório
4. Não pode haver duplicação de números na raiz
5. O core deve permanecer isolado e independente dos diretórios auxiliares
6. Nenhuma lógica de negócio deve estar fora do core
