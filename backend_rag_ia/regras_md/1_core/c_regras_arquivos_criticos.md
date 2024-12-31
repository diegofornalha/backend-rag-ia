# Arquivos Críticos do Projeto

## 🚨 Definição

Arquivos críticos são componentes essenciais do sistema que requerem atenção especial devido ao seu impacto direto no funcionamento da aplicação.

## ⚠️ Arquivos Críticos Atuais

### 1. `app_server.py`

- **Função**: Configuração e inicialização do servidor FastAPI
- **Impacto**: Afeta toda a aplicação
- **Localização**: `/backend-rag-ia/cli/`
- **Cuidados Especiais**:
  - Alterações devem ser testadas em ambiente de desenvolvimento
  - Requer revisão de código por pelo menos dois desenvolvedores
  - Mudanças devem ser documentadas detalhadamente
  - Backup obrigatório antes de modificações

## 📋 Regras para Arquivos Críticos

### 1. Modificações

- Criar branch específica para alterações
- Realizar testes completos antes do merge
- Documentar todas as mudanças
- Notificar equipe sobre alterações

### 2. Revisão

- Code review obrigatório
- Testes de integração necessários
- Validação em ambiente de staging

### 3. Backup

- Manter versão de backup antes de alterações
- Documentar procedimento de rollback
- Testar processo de restauração

### 4. Monitoramento

- Logs detalhados de alterações
- Monitoramento de performance
- Alertas para erros críticos

### 5. Documentação

- Manter documentação atualizada
- Registrar todas as dependências
- Documentar configurações necessárias

## 🔄 Processo de Atualização da Lista

1. Identificar arquivos críticos novos
2. Avaliar impacto no sistema
3. Documentar responsabilidades
4. Atualizar esta documentação

## 📝 Observações

- Esta lista deve ser revisada mensalmente
- Novos arquivos críticos devem ser adicionados conforme identificados
- Manter histórico de alterações em arquivos críticos

## 📚 Padrão para Novas Regras

### Formato Obrigatório

1. **Identificação do Arquivo**:

   ```markdown
   ### N. `nome_do_arquivo.ext`
   ```

2. **Metadados Obrigatórios**:

   ```markdown
   - **Função**: Descrição clara da responsabilidade
   - **Impacto**: Áreas/componentes afetados
   - **Localização**: Caminho completo no projeto
   ```

3. **Cuidados Especiais**:
   ```markdown
   - **Cuidados Especiais**:
     - Lista de cuidados específicos
     - Requisitos de segurança
     - Procedimentos especiais
   ```

### Exemplo de Nova Regra:

```markdown
### 2. `config.py`

- **Função**: Gerenciamento de configurações globais
- **Impacto**: Sistema completo
- **Localização**: `/backend-rag-ia/config/`
- **Cuidados Especiais**:
  - Validar todas as variáveis de ambiente
  - Testar em todos os ambientes
  - Documentar cada configuração
```
