# Regras de Organização SQL

## 📁 Estrutura de Diretórios e Arquivos

### 1. /sql/setup/

```
a. init.sql
   - Configurações iniciais do PostgreSQL
   - Extensões básicas
   - Configurações de timezone e locale

b. setup_env_render.sql
   - Configurações específicas do Render
   - Variáveis de ambiente
   - Limites e otimizações

c. setup_embeddings.sql
   - Configuração da extensão vector
   - Funções de embedding
   - Índices de similaridade

d. base_conhecimento_geral_01.sql
   - Estrutura da base de conhecimento
   - Índices e triggers
   - Funções de busca
```

### 2. /sql/security/

```
a. roles.sql
   - Definição de roles
   - Permissões básicas
   - Grupos de usuários

b. policies.sql
   - Row Level Security (RLS)
   - Políticas de acesso
   - Restrições de segurança

c. auth.sql
   - Funções de autenticação
   - Tokens e sessões
   - Validações de acesso
```

### 3. /sql/migrations/

```
a. 001_initial_schema.sql
   - Estrutura inicial do banco
   - Tabelas principais
   - Relacionamentos base

b. 002_add_embeddings.sql
   - Suporte a embeddings
   - Índices vetoriais
   - Funções de similaridade

c. 003_security_layer.sql
   - Implementação de RLS
   - Políticas de segurança
   - Roles e permissões
```

### 4. /sql/maintenance/

```
a. vacuum.sql
   - Scripts de limpeza
   - Otimização de tabelas
   - Recuperação de espaço

b. monitoring.sql
   - Funções de monitoramento
   - Alertas e logs
   - Métricas de performance

c. backup.sql
   - Rotinas de backup
   - Restauração
   - Verificação de integridade
```

## 🔄 Ordem de Execução

1. **Setup (Obrigatório)**

   ```sql
   \i sql/setup/a_init.sql
   \i sql/setup/b_setup_env_render.sql
   \i sql/setup/c_setup_embeddings.sql
   \i sql/setup/d_base_conhecimento_geral_01.sql
   ```

2. **Security (Crítico)**

   ```sql
   \i sql/security/a_roles.sql
   \i sql/security/b_policies.sql
   \i sql/security/c_auth.sql
   ```

3. **Migrations (Sequencial)**

   ```sql
   \i sql/migrations/a_001_initial_schema.sql
   \i sql/migrations/b_002_add_embeddings.sql
   \i sql/migrations/c_003_security_layer.sql
   ```

4. **Maintenance (Configuração)**
   ```sql
   \i sql/maintenance/a_vacuum.sql
   \i sql/maintenance/b_monitoring.sql
   \i sql/maintenance/c_backup.sql
   ```

## ⚠️ Regras Críticas SQL

1. **Extensões**

   - Vector DEVE ser instalada primeiro
   - pgcrypto é OBRIGATÓRIO para segurança
   - pg_stat_statements para monitoramento

2. **Segurança**

   - RLS DEVE ser habilitado
   - Políticas DEVEM ser testadas
   - Roles com privilégios mínimos

3. **Performance**
   - Índices DEVEM ser criados
   - VACUUM configurado
   - Monitoramento ativo

## 🔍 Validações SQL

### Pré-execução

```sql
-- Verificar extensões
SELECT extname, extversion FROM pg_extension;

-- Verificar roles
SELECT rolname, rolsuper FROM pg_roles;

-- Verificar tabelas
\dt
```

### Pós-execução

```sql
-- Verificar índices
SELECT schemaname, tablename, indexname FROM pg_indexes;

-- Verificar políticas
SELECT * FROM pg_policies;

-- Verificar conexões
SELECT * FROM pg_stat_activity;
```

## 📝 Padrões SQL

1. **Nomenclatura**

   - Tabelas: snake_case
   - Funções: camelCase
   - Índices: idx_tabela_coluna

2. **Comentários**

   ```sql
   -- Seção principal
   /*
    * Descrição detalhada
    * Múltiplas linhas
    */
   ```

3. **Formatação**
   ```sql
   SELECT
       coluna1,
       coluna2
   FROM tabela
   WHERE condição;
   ```

## 🚨 Tratamento de Erros SQL

1. **Transações**

   ```sql
   BEGIN;
   -- operações
   EXCEPTION WHEN OTHERS THEN
   ROLLBACK;
   -- log do erro
   END;
   ```

2. **Logs**

   ```sql
   CREATE TABLE rag.error_log (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       tipo TEXT NOT NULL,
       mensagem TEXT NOT NULL,
       detalhes JSONB,
       criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
   );

   -- Habilitar RLS
   ALTER TABLE rag.error_log ENABLE ROW LEVEL SECURITY;

   -- Criar políticas de acesso
   CREATE POLICY "Permitir select para authenticated"
   ON rag.error_log
   FOR SELECT
   TO authenticated
   USING (true);

   CREATE POLICY "Permitir insert para service_role"
   ON rag.error_log
   FOR INSERT
   TO service_role
   WITH CHECK (true);

   CREATE POLICY "Permitir delete para service_role"
   ON rag.error_log
   FOR DELETE
   TO service_role
   USING (true);
   ```

## 🔄 Manutenção SQL

1. **Rotina Diária**

   ```sql
   -- Vacuum automático
   -- Análise de performance
   -- Backup incremental
   ```

2. **Rotina Semanal**
   ```sql
   -- Vacuum full
   -- Backup completo
   -- Análise de índices
   ```

## 📦 Processo de Reorganização

### 1. Análise Inicial

```bash
# 1.1 Verificar estrutura atual
- Listar todas as pastas
- Identificar arquivos existentes
- Mapear dependências

# 1.2 Planejar reorganização
- Definir nova estrutura
- Mapear renomeações necessárias
- Identificar arquivos a serem criados
```

### 2. Reorganização de Diretórios

```bash
# 2.1 Renomear pastas principais (ordem obrigatória)
mv setup 1_setup
mv security 2_security
mv migrations 3_migrations
mv maintenance 4_maintenance

# 2.2 Verificar permissões
- Garantir acesso de escrita
- Manter permissões originais
- Verificar proprietário dos arquivos
```

### 3. Reorganização de Arquivos

```bash
# 3.1 Setup (1_setup/)
mv init.sql a_init.sql
mv setup_env_render.sql b_setup_env_render.sql
mv setup_embeddings.sql c_setup_embeddings.sql
mv base_conhecimento_geral_01.sql d_base_conhecimento_geral_01.sql

# 3.2 Security (2_security/)
mv setup_security.sql a_roles.sql
touch b_policies.sql
touch c_auth.sql

# 3.3 Migrations (3_migrations/)
mv reorganize_schemas.sql a_001_initial_schema.sql
mv separar_embeddings.sql b_002_add_embeddings.sql
mv adicionar_document_hash.sql c_003_security_layer.sql

# 3.4 Maintenance (4_maintenance/)
mv setup_maintenance.sql a_vacuum.sql
mv analyze_tables.sql b_monitoring.sql
mv limpar_referencias_antigas.sql c_backup.sql
```

### 4. Validação Pós-Reorganização

```bash
# 4.1 Verificar estrutura
- Confirmar renomeação das pastas
- Verificar arquivos em cada pasta
- Validar nomenclatura

# 4.2 Testar integridade
- Verificar referências nos arquivos
- Testar scripts de execução
- Validar dependências
```

### 5. Ordem de Execução Pós-Reorganização

```sql
-- 5.1 Setup
\i sql/1_setup/a_init.sql
\i sql/1_setup/b_setup_env_render.sql
\i sql/1_setup/c_setup_embeddings.sql
\i sql/1_setup/d_base_conhecimento_geral_01.sql

-- 5.2 Security
\i sql/2_security/a_roles.sql
\i sql/2_security/b_policies.sql
\i sql/2_security/c_auth.sql

-- 5.3 Migrations
\i sql/3_migrations/a_001_initial_schema.sql
\i sql/3_migrations/b_002_add_embeddings.sql
\i sql/3_migrations/c_003_security_layer.sql

-- 5.4 Maintenance
\i sql/4_maintenance/a_vacuum.sql
\i sql/4_maintenance/b_monitoring.sql
\i sql/4_maintenance/c_backup.sql
```

### ⚠️ Regras Críticas de Reorganização

1. **Ordem de Execução**

   - SEMPRE começar pelas pastas (top-down)
   - NUNCA renomear arquivos antes das pastas
   - Manter backup antes de iniciar

2. **Nomenclatura**

   - Pastas: Número_nome (1_setup)
   - Arquivos: Letra_nome (a_init.sql)
   - Manter consistência em todo projeto

3. **Validações**

   - Verificar antes de cada etapa
   - Validar após cada mudança
   - Documentar alterações

4. **Dependências**
   - Mapear referências entre arquivos
   - Atualizar caminhos nos scripts
   - Testar integridade após mudanças

### 🔍 Checklist de Reorganização

#### Pré-reorganização

- [ ] Backup completo realizado
- [ ] Estrutura atual mapeada
- [ ] Dependências identificadas
- [ ] Plano de reorganização definido

#### Durante reorganização

- [ ] Renomeação de pastas concluída
- [ ] Arquivos movidos corretamente
- [ ] Nomenclatura padronizada
- [ ] Permissões mantidas

#### Pós-reorganização

- [ ] Estrutura final validada
- [ ] Scripts de execução testados
- [ ] Documentação atualizada
- [ ] Equipe notificada das mudanças
