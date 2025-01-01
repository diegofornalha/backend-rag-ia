# Regras para Execução de SQL no Editor Supabase

Este documento descreve as regras e procedimentos para executar comandos SQL no Editor do Supabase.

## Arquivos SQL Disponíveis

### 1. init.sql

- Arquivo principal de inicialização
- Cria a extensão pgvector
- Define a tabela de documentos
- Configura funções básicas de embedding e busca

### 2. setup_embeddings.sql

- Configuração específica para embeddings
- Gerenciamento de integridade dos embeddings
- Triggers para manutenção automática

### 3. setup_search.sql

- Configuração da funcionalidade de busca
- Funções de matching e similaridade
- Otimizações de performance para buscas

### 4. setup_maintenance.sql (NOVO)

- Funções de manutenção e limpeza
- Remoção de documentos antigos
- Limpeza de embeddings órfãos
- Atualização automática de timestamps

### 5. setup_metrics.sql (NOVO)

- Funções para métricas e monitoramento
- Estatísticas do sistema
- Qualidade dos embeddings
- Performance das buscas

### 6. setup_security.sql (NOVO)

- Configurações de Row Level Security (RLS)
- Políticas de acesso para documentos
- Políticas de acesso para embeddings
- Controle de permissões por usuário

## Procedimento de Atualização

1. Abra o Editor SQL no Supabase
2. Copie o conteúdo do arquivo SQL desejado
3. Cole no Editor SQL
4. Execute os comandos
5. Verifique se não houve erros

⚠️ IMPORTANTE: Sempre que houver atualizações nos arquivos SQL locais, é necessário atualizar manualmente no Editor SQL do Supabase.

## Ordem de Execução Recomendada

1. init.sql
2. setup_embeddings.sql
3. setup_search.sql
4. setup_maintenance.sql
5. setup_metrics.sql
6. setup_security.sql

## Verificação

Após executar os comandos, você pode verificar se as funções foram criadas corretamente usando:

```sql
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
ORDER BY routine_name;
```

Para verificar as políticas RLS:

```sql
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE schemaname = 'public';
```

## Resolução de Problemas

Se encontrar o erro "cannot change return type of existing function":

1. Primeiro execute o comando DROP FUNCTION correspondente
2. Em seguida, crie a função novamente

Exemplo:

```sql
DROP FUNCTION IF EXISTS nome_da_funcao;
-- Então execute o CREATE FUNCTION
```

Para problemas com RLS:

1. Verifique se RLS está habilitado:

```sql
SELECT relname, relrowsecurity
FROM pg_class
WHERE relname = 'documentos';
```

2. Se precisar remover uma política:

```sql
DROP POLICY IF EXISTS nome_da_politica ON nome_da_tabela;
```
