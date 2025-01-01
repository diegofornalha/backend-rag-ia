# Diretrizes de Hierarquia e Organização

## Estrutura de Diretórios

### 1. Diretório Core

O diretório core é o único que não segue o padrão numérico na raiz:

```
backend_rag_ia/           # Core da aplicação
├── api/                  # Endpoints da API
├── config/              # Configurações
├── models/              # Modelos de dados
├── services/            # Serviços principais
└── utils/               # Utilitários core
```

### 2. Diretórios Raiz

Todos os outros diretórios na raiz seguem o padrão numérico:

```
/
├── backend_rag_ia/          # Core (exceção ao padrão)
├── 01_regras_md_apenas_raiz/# Documentação e regras
├── 02_logs_apenas_raiz/     # Logs da aplicação
├── 03_monitoring_apenas_raiz/# Monitoramento
├── 04_scripts_apenas_raiz/  # Scripts utilitários
├── 05_sql_apenas_raiz/      # Scripts SQL
└── 06_testes_apenas_raiz/   # Testes automatizados
```

## Hierarquia de Documentação

### 1. Documentação Crítica (Prioridade 1)

Localização: `01_regras_md_apenas_raiz/1_core/`

- `a_readme.md` - Visão geral do projeto
- `g_regras_avaliacao_core.md` - Regras do core
- `h_diretrizes_hierarquia.md` - Esta documentação

### 2. Documentação de Desenvolvimento (Prioridade 2)

Localização: `01_regras_md_apenas_raiz/4_development/`

- `a_index.md` - Índice geral
- `b_tasks.md` - Tarefas e organização
- `c_regras.md` - Regras gerais

### 3. Documentação de Banco de Dados (Prioridade 3)

Localização: `01_regras_md_apenas_raiz/2_database/`

- Configurações
- Migrações
- Modelos

### 4. Documentação de Deploy (Prioridade 4)

Localização: `01_regras_md_apenas_raiz/3_deployment/`

- Processos
- Ambientes
- Configurações

### 5. Documentação de Monitoramento (Prioridade 5)

Localização: `01_regras_md_apenas_raiz/5_monitoring/`

- Métricas
- Alertas
- Logs

### 6. Documentação de Melhorias (Prioridade 6)

Localização: `01_regras_md_apenas_raiz/6_melhorias/`

- Propostas
- Roadmap
- Experimentos

## Regras de Nomenclatura

### 1. Diretórios Raiz

- Formato: `NN_nome_apenas_raiz`
- Exemplo: `01_regras_md_apenas_raiz`
- Exceção: `backend_rag_ia` (core)

### 2. Subdiretórios

- Formato: `N_nome_categoria`
- Exemplo: `1_core`, `2_database`

### 3. Arquivos

- Formato: `letra_nome_arquivo.extensão`
- Exemplo: `a_readme.md`, `b_tasks.md`

## Ordem de Importância

1. Core da Aplicação

   - `backend_rag_ia/`
   - Funcionalidades essenciais
   - Serviços principais

2. Documentação e Regras

   - `01_regras_md_apenas_raiz/`
   - Documentação crítica
   - Padrões e diretrizes

3. Logs e Monitoramento

   - `02_logs_apenas_raiz/`
   - `03_monitoring_apenas_raiz/`
   - Observabilidade

4. Ferramentas e Scripts

   - `04_scripts_apenas_raiz/`
   - Utilitários
   - Automações

5. Banco de Dados

   - `05_sql_apenas_raiz/`
   - Scripts SQL
   - Migrações

6. Testes
   - `06_testes_apenas_raiz/`
   - Testes automatizados
   - Fixtures

## Manutenção da Hierarquia

### 1. Revisão Regular

- Verificar estrutura periodicamente
- Ajustar numeração conforme necessário
- Atualizar documentação

### 2. Adição de Novos Componentes

- Seguir padrão numérico
- Manter ordem lógica
- Documentar mudanças

### 3. Refatoração

- Respeitar hierarquia
- Manter consistência
- Atualizar referências
