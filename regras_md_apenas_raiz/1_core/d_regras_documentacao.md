# Regras de Documentação

## 1. Formatação de Arquivos Markdown

### 1.1 Codificação e Caracteres

- Todos os arquivos devem usar codificação UTF-8
- Não deve haver BOM (Byte Order Mark) no início dos arquivos
- Evitar caracteres de controle, exceto quebras de linha
- Usar LF (\n) para quebras de linha, não CRLF (\r\n)

### 1.2 Estrutura do Documento

- Usar títulos com # (h1) para o título principal
- Subtítulos devem seguir hierarquia (##, ###, etc)
- Manter uma linha em branco entre seções
- Usar listas com - para itens não ordenados
- Usar listas com 1. para itens ordenados

### 1.3 Metadados

- Cada documento deve ter um título único e descritivo
- Incluir categoria/seção no caminho do arquivo
- Manter consistência na nomenclatura dos arquivos

## 2. Boas Práticas

### 2.1 Conteúdo

- Usar linguagem clara e objetiva
- Manter parágrafos concisos
- Incluir exemplos quando relevante
- Evitar repetição de informações

### 2.2 Organização

- Agrupar informações relacionadas
- Usar seções lógicas e bem definidas
- Manter consistência no estilo de formatação
- Atualizar documentação quando houver mudanças

### 2.3 Versionamento

- Documentar alterações significativas
- Manter histórico de atualizações
- Incluir data de última modificação
- Sincronizar documentação com código

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

## Padrão de Nomenclatura

### Arquivos em Diretórios

- Usar prefixo alfabético sequencial (a*, b*, c\_, etc.)
- Nomes em minúsculas com underscores
- Exemplo de sequência em um diretório:
  ```
  2_database/
  ├── a_initial_schema.sql
  ├── b_add_embeddings.sql
  ├── c_security_layer.sql
  ├── d_move_schema.sql
  ├── e_regras_supabase.md
  └── f_problemas_docker.md
  ```
- Ao adicionar novo arquivo, usar a próxima letra disponível na sequência
- Manter ordem alfabética para facilitar navegação e manutenção
