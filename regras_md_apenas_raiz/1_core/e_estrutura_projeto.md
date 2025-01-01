# Estrutura do Projeto Python

## 1. Organização de Módulos

### 1.1 Estrutura Básica

```
backend_rag_ia/
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── search.py
│   └── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
└── services/
    ├── __init__.py
    └── semantic_search.py
```

### 1.2 Arquivos Essenciais

- `__init__.py` em cada diretório
- `main.py` como ponto de entrada
- `settings.py` para configurações

## 2. Boas Práticas

### 2.1 Importações

- Usar importações relativas quando apropriado
- Evitar importações circulares
- Organizar imports por tipo

### 2.2 Configurações

- Usar Pydantic para validação
- Centralizar configurações
- Documentar variáveis de ambiente

## 3. Validações e Testes

### 3.1 Validação de Dados

- Implementar schemas Pydantic
- Validar inputs de API
- Tratar erros adequadamente

### 3.2 Logging

- Configurar logs estruturados
- Definir níveis de log apropriados
- Incluir contexto nos logs

## 4. Desenvolvimento

### 4.1 Ambiente Virtual

- Usar virtualenv ou venv
- Manter requirements.txt atualizado
- Documentar dependências

### 4.2 Debugging

- Configurar debug mode
- Usar ferramentas de profiling
- Monitorar performance
