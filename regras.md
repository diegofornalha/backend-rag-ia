# Regras de Documentação

## 1. Regras Obrigatórias

### 1.1 Idioma e Localização

- [x] Respostas sempre em português BR
- [x] Considerar ambiente Mac para comandos e configurações

### 1.2 Arquitetura e Organização

- [x] Manter boas práticas de aplicação server-side
- [x] Separar responsabilidades entre backend e frontend
- [x] Evitar conteúdo misto (server-side/client-side)
- [x] Verificar duplicidade antes de criar novos arquivos

## 2. Convenções de Código

### 2.1 Estilo e Formatação

- [x] Seguir PEP 8 para Python
- [x] Usar type hints
- [x] Documentar funções e classes
- [x] Manter consistência na nomenclatura

### 2.2 Organização de Arquivos

- [x] Estrutura clara de diretórios
- [x] Separação por funcionalidade
- [x] Nomes descritivos e significativos

## 3. Regras de Execução

### 3.1 Comandos e Instalações

- [x] Executar comandos da allowlist diretamente
  - Exemplo: `pnpm install`
  - Exemplo: `npm install -g`
- [x] Iniciar instalações no composer
  - Exemplo: `/bin/bash`
  - Exemplo: `brew install node`

### 3.2 Comportamento

- ❌ Não perguntar permissão para continuar
- ❌ Não pedir confirmação para instalação
- ✅ Executar comandos em sequência
- ✅ Prosseguir automaticamente quando necessário

## 4. Regras de Preservação

### 4.1 Proteção de Funcionalidades

- ⚠️ IMPORTANTE: Antes de remover qualquer funcionalidade ou endpoint:
  1. **PARE IMEDIATAMENTE** se a funcionalidade tiver utilidade prática
  2. **CONSULTE** o desenvolvedor sobre a remoção
  3. **EXPLIQUE** claramente a utilidade da funcionalidade
  4. **AGUARDE** confirmação explícita antes de prosseguir

### 4.2 Versionamento e Backup

- [x] Manter histórico de alterações
- [x] Documentar mudanças significativas
- [x] Criar backups antes de alterações críticas

## 5. Integração e Deploy

### 5.1 Testes e Qualidade

- [x] Executar testes antes do deploy
- [x] Verificar qualidade do código
- [x] Validar integrações

### 5.2 Processo de Deploy

- [x] Seguir checklist de deploy
- [x] Monitorar processo
- [x] Documentar problemas e soluções
