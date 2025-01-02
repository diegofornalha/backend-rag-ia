# Estrutura de Diretórios do Projeto

## Visão Geral

O projeto está organizado em duas categorias principais:

1. Core do Backend (sem prefixo numérico)
2. Diretórios Auxiliares (com prefixos numéricos por prioridade)

## Core do Backend (backend_core/)

Contém toda a lógica de negócio e regras principais do sistema:

```
backend_core/
├── models/         # Modelos de dados e entidades
├── services/       # Serviços e lógica de negócio
├── business_rules/ # Regras de negócio específicas
└── exceptions/     # Tratamento de exceções
```

## Diretórios Auxiliares

### 00_testes_apenas_raiz/

Prioridade máxima - Testes e qualidade do código

```
├── unit/          # Testes unitários
├── integration/   # Testes de integração
└── monitoring/    # Monitoramento e performance
```

### 01_ferramentas_rag/

Ferramentas essenciais após testes

```
└── cli/
    ├── utils/     # Utilitários e helpers
    └── dados/     # Dados para ferramentas RAG
```

### 02_documentacao/

Documentação do projeto

```
├── docs/          # Documentação geral
└── schemas/       # Schemas e definições
```

### 03_dados/

Dados e recursos do projeto

```
├── fixtures/      # Dados de teste
└── embates/       # Registros de embates e decisões
```

## Regras de Organização

1. O core do backend (backend_core/) é o único diretório sem prefixo numérico
2. Todos os outros diretórios seguem o padrão XX\_ onde XX é um número que indica prioridade
3. Quanto menor o número, maior a prioridade do diretório
4. O core deve permanecer isolado e independente dos diretórios auxiliares
5. Nenhuma lógica de negócio deve estar fora do core
