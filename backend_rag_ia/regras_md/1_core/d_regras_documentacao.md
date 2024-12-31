# Regras de Documentação

## 1. Quando Dividir Arquivos

### Indicadores para Divisão

1. **Tamanho do Arquivo**:

   - Mais de 200 linhas
   - Mais de 3 níveis de hierarquia
   - Scroll excessivo para encontrar informação

2. **Complexidade**:

   - Muitos exemplos de código
   - Múltiplos fluxos ou processos
   - Diferentes contextos técnicos

3. **Frequência de Atualização**:
   - Seções que mudam frequentemente
   - Partes que precisam de revisão separada
   - Conteúdo mantido por times diferentes

### Quando NÃO Dividir

1. **Conteúdo Coeso**:

   - Tópico único e bem definido
   - Menos de 150 linhas
   - Dependências diretas entre seções

2. **Documentação Inicial**:
   - Projetos em fase inicial
   - Conceitos ainda em desenvolvimento
   - Processos não estabilizados

## 2. Como Dividir

### Estrutura Recomendada

1. **Arquivo Principal**:

   ```markdown
   # Tema Principal

   > ⚠️ Índice e visão geral

   ## 1. Visão Geral

   - Objetivo
   - Contexto
   - Stack

   ## 2. Documentos Relacionados

   1. [Tópico A](./subdir/TOPICO_A.md)
   2. [Tópico B](./subdir/TOPICO_B.md)

   ## 3. Regras Essenciais

   - Regras críticas
   - Diretrizes principais
   ```

2. **Arquivos Específicos**:

   ```markdown
   # Tópico Específico

   ## 1. Detalhes

   - Informações específicas
   - Exemplos
   - Casos de uso
   ```

### Organização de Diretórios

```
regras_md/
├── REGRAS_PRINCIPAL.md
└── topico/
    ├── DETALHES.md
    ├── CONFIGURACAO.md
    └── PROBLEMAS.md
```

## 3. Boas Práticas

### Nomes de Arquivos

1. **Formato**:

   - MAIÚSCULAS para arquivos principais
   - Usar underline (\_) para separar palavras
   - Extensão .md para markdown

2. **Convenções**:
   - Prefixo REGRAS\_ para regras
   - Prefixo DOC\_ para documentação
   - Sufixo \_EXEMPLO para exemplos

### Links e Referências

1. **Entre Arquivos**:

   - Usar links relativos
   - Manter hierarquia clara
   - Atualizar links ao mover arquivos

2. **Manutenção**:
   - Verificar links quebrados
   - Manter índice atualizado
   - Documentar dependências

## 4. Métricas para Decisão

### Quando Dividir

✅ **DIVIDIR se**:

- Arquivo > 200 linhas
- > 3 níveis de hierarquia
- Múltiplos contextos técnicos
- Atualizações frequentes em partes específicas
- Diferentes responsáveis por manutenção

❌ **NÃO DIVIDIR se**:

- Arquivo < 150 linhas
- Tópico único e coeso
- Dependências fortes entre seções
- Projeto em fase inicial
- Processo ainda não estável
