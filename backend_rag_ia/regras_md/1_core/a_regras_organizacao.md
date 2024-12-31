# Regras de Organização do Projeto

## 📚 Princípios Fundamentais

1. **Hierarquia Clara**

   - Usar numeração para indicar ordem de importância
   - Usar letras para subcomponentes
   - Manter consistência na nomenclatura

2. **Dependências**
   - Respeitar ordem de execução
   - Documentar dependências entre componentes
   - Validar requisitos antes da execução

## 🗂️ Estrutura de Diretórios

### 1. Setup (Configuração Base)

```
📁 1. /setup/
   a. init.[extensão] (Configurações iniciais)
   b. env.[extensão] (Variáveis de ambiente)
   c. core.[extensão] (Funcionalidades core)
   d. base.[extensão] (Estruturas base)
```

### 2. Security (Segurança)

```
📁 2. /security/
   a. roles.[extensão] (Papéis e permissões)
   b. policies.[extensão] (Políticas de acesso)
   c. auth.[extensão] (Autenticação)
```

### 3. Migrations (Migrações)

```
📁 3. /migrations/
   a. 001_initial.[extensão]
   b. 002_features.[extensão]
   c. 003_updates.[extensão]
```

### 4. Maintenance (Manutenção)

```
📁 4. /maintenance/
   a. cleanup.[extensão]
   b. monitoring.[extensão]
   c. backup.[extensão]
```

## 🔄 Ordem de Execução

1. **Sequência Obrigatória**

   ```
   1. SETUP → 2. SECURITY → 3. MIGRATIONS → 4. MAINTENANCE
   ```

2. **Validações**
   - Verificar conclusão de cada etapa
   - Confirmar integridade
   - Registrar execução

## ⚠️ Regras Críticas

1. **NUNCA**

   - Pular etapas da sequência
   - Misturar responsabilidades entre diretórios
   - Ignorar validações

2. **SEMPRE**
   - Seguir a numeração estabelecida
   - Documentar alterações
   - Manter logs de execução

## 📋 Padrões de Nomenclatura

1. **Diretórios**

   - Usar números para ordem: `1_setup`, `2_security`
   - Nomes em minúsculas
   - Separar palavras com underscore

2. **Arquivos**
   - Usar letras para subcomponentes: `a_init.sql`, `b_env.sql`
   - Nomes descritivos
   - Incluir versão quando aplicável

## 🔍 Validações e Checklist

### Pré-execução

- [ ] Verificar dependências
- [ ] Confirmar ordem de execução
- [ ] Validar permissões

### Durante execução

- [ ] Monitorar logs
- [ ] Verificar integridade
- [ ] Registrar progresso

### Pós-execução

- [ ] Confirmar conclusão
- [ ] Validar funcionamento
- [ ] Atualizar documentação

## 📝 Documentação

1. **Obrigatório Documentar**

   - Propósito de cada diretório
   - Dependências entre componentes
   - Ordem de execução
   - Alterações realizadas

2. **Formato de Documentação**

   ```markdown
   # Nome do Componente

   ## Objetivo

   ## Dependências

   ## Ordem de Execução

   ## Notas Importantes
   ```

## 🚨 Tratamento de Erros

1. **Em caso de falha**

   - Interromper sequência
   - Registrar erro
   - Reverter alterações se necessário

2. **Recuperação**
   - Identificar ponto de falha
   - Corrigir problema
   - Reiniciar da última etapa válida

## 🔄 Manutenção

1. **Rotina**

   - Verificar logs periodicamente
   - Atualizar documentação
   - Validar integridade

2. **Atualizações**
   - Seguir ordem numérica
   - Documentar mudanças
   - Testar em ambiente isolado

## 👥 Colaboração

1. **Regras para Equipe**

   - Seguir padrões estabelecidos
   - Documentar alterações
   - Comunicar mudanças críticas

2. **Code Review**
   - Verificar ordem de execução
   - Validar nomenclatura
   - Confirmar documentação

## 🎯 Benefícios

1. **Organização**

   - Estrutura clara e consistente
   - Fácil manutenção
   - Melhor rastreabilidade

2. **Segurança**

   - Execução controlada
   - Validações em cada etapa
   - Recuperação de falhas

3. **Eficiência**
   - Processo padronizado
   - Menos erros
   - Maior produtividade

## 📈 Evolução do Projeto

1. **Versionamento**

   - Seguir semântica de versões
   - Documentar mudanças
   - Manter histórico

2. **Melhorias**
   - Coletar feedback
   - Implementar otimizações
   - Atualizar documentação

## 📁 Regras de Subpastas

### ⚠️ Regra Crítica: Sem Arquivos Soltos

1. **Princípio Fundamental**

   ```
   ❌ NUNCA deixar arquivos soltos na raiz das pastas principais
   ✅ SEMPRE organizar arquivos em subpastas apropriadas
   ```

2. **Estrutura Correta**

   ```
   pasta_principal/
   ├── 1_subpasta/
   │   └── arquivos...
   ├── 2_subpasta/
   │   └── arquivos...
   └── 3_subpasta/
       └── arquivos...
   ```

3. **Estrutura Incorreta**
   ```
   pasta_principal/
   ├── arquivo_solto.ext    ❌
   ├── outro_arquivo.ext    ❌
   └── 1_subpasta/
       └── arquivos...
   ```

### 🔄 Aplicação da Regra

1. **Para Regras e Documentação**

   ```
   regras_md/
   ├── 1_core/
   │   └── REGRAS_CORE.md
   ├── 2_database/
   │   └── REGRAS_SQL.md
   ├── 3_development/
   │   └── REGRAS_DEV.md
   ├── 4_deployment/
   │   └── REGRAS_DEPLOY.md
   └── 5_monitoring/
       └── REGRAS_MONITOR.md
   ```

2. **Para Código SQL**
   ```
   sql/
   ├── 1_setup/
   │   └── arquivos...
   ├── 2_security/
   │   └── arquivos...
   ├── 3_migrations/
   │   └── arquivos...
   └── 4_maintenance/
       └── arquivos...
   ```

### 🎯 Benefícios

1. **Organização**

   - Estrutura mais limpa
   - Melhor navegabilidade
   - Facilita manutenção

2. **Padronização**

   - Consistência no projeto
   - Fácil localização
   - Melhor escalabilidade

3. **Colaboração**
   - Reduz confusão
   - Facilita revisão
   - Melhora documentação

### ✅ Checklist de Conformidade

- [ ] Nenhum arquivo na raiz das pastas principais
- [ ] Todos os arquivos organizados em subpastas
- [ ] Subpastas seguem padrão numérico
- [ ] Documentação reflete estrutura atual
