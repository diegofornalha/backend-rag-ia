# Problemas Conhecidos

## Problemas de Linting (Ruff)

### 1. Importações e Organização de Código

- **Ordem de Importações (I001)**

  - Alguns arquivos apresentam importações fora de ordem
  - Afeta principalmente arquivos CLI como `gerar_relatorio_ruff.py` e `subir_para_supabase.py`
  - Solução: Organizar imports seguindo a ordem: stdlib, third-party, local

- **Importações no Nível do Módulo (E402)**
  - Importações após código executável
  - Ocorre em scripts que manipulam `sys.path`
  - Solução: Mover importações para o topo do arquivo quando possível

### 2. Tratamento de Exceções

- **Bare Except (E722)**

  - Blocos `except` sem especificação do tipo de exceção
  - Encontrado em scripts de monitoramento e controle
  - Solução: Especificar tipos de exceção apropriados

- **Rastreamento de Exceções (B904)**
  - Exceções levantadas sem usar `from` para preservar o rastreamento
  - Afeta rotas de API e handlers de erro
  - Solução: Usar `raise ... from err` para manter o contexto da exceção

### 3. Código Não Utilizado

- **Variáveis Não Utilizadas (F841)**

  - Variáveis atribuídas mas nunca usadas em blocos `except`
  - Comum em handlers de erro e logs
  - Solução: Remover variáveis não utilizadas ou usar `_` para indicar intencionalmente não usado

- **Imports Não Utilizados (F401)**
  - Módulos importados mas não utilizados no código
  - Encontrado em vários arquivos CLI
  - Solução: Remover imports não utilizados ou documentar por que são necessários

### 4. Formatação e Estilo

- **Espaços em Branco (W293)**

  - Linhas em branco contendo espaços
  - Presente em vários arquivos do projeto
  - Solução: Remover espaços em branco de linhas vazias

- **F-strings Sem Placeholders (F541)**
  - F-strings usadas sem variáveis para interpolação
  - Encontrado em mensagens de log e console
  - Solução: Usar strings normais quando não houver interpolação

### 5. Complexidade de Código

- **Complexidade de Funções (C901)**
  - Funções muito complexas com muitos caminhos de execução
  - Principalmente em funções `main()` e handlers de upload
  - Solução: Refatorar em funções menores e mais focadas

## Recomendações Gerais

1. Executar `ruff check .` regularmente durante o desenvolvimento
2. Usar `ruff check . --fix` para correções automáticas
3. Manter um arquivo `.ruff.toml` atualizado com as configurações do projeto
4. Documentar exceções às regras quando necessário

## Status Atual

- Total de problemas identificados: 415
- Problemas fixáveis automaticamente: 301
- Problemas que requerem intervenção manual: 114

**Nota**: Alguns destes problemas são intencionais devido à natureza específica do código ou requisitos do projeto. Estes casos devem ser documentados no arquivo de configuração do Ruff.
