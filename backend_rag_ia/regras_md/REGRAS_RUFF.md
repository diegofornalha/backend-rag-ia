# Regras de Execução do Ruff

## Regra de Dupla Verificação

1. **Primeira Execução**:

   - Executar o Ruff para identificar problemas iniciais
   - Corrigir todos os problemas encontrados
   - Documentar as correções realizadas

2. **Segunda Execução**:

   - Executar o Ruff novamente para garantir que:
     - As correções não introduziram novos problemas
     - Todos os problemas foram realmente resolvidos
   - Se novos problemas forem encontrados, voltar ao passo 1

3. **Critérios de Sucesso**:
   - O script só é considerado validado quando:
     - Duas execuções consecutivas do Ruff não apresentarem erros
     - Todas as correções foram documentadas
     - Nenhum novo problema foi introduzido

## Regras de Correção

1. **Priorização**:

   - Corrigir primeiro problemas críticos (erros)
   - Em seguida, corrigir warnings
   - Por último, aplicar melhorias de estilo

2. **Documentação**:

   - Registrar cada tipo de problema encontrado
   - Documentar a solução aplicada
   - Manter histórico das alterações

3. **Validação**:
   - Testar o código após cada conjunto de correções
   - Garantir que as funcionalidades não foram afetadas
   - Verificar se as correções seguem as boas práticas

## Exceções

1. **Falsos Positivos**:

   - Documentar claramente por que a regra não se aplica
   - Adicionar comentário no código explicando a exceção
   - Atualizar configuração do Ruff se necessário

2. **Conflitos**:
   - Em caso de conflito entre regras, priorizar:
     1. Segurança
     2. Funcionalidade
     3. Manutenibilidade
     4. Estilo

## Configuração do Ruff

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

# Regras habilitadas
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "YTT", # flake8-2020
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "DTZ", # flake8-datetimez
    "ISC", # flake8-implicit-str-concat
    "PIE", # flake8-pie
    "T20", # flake8-print
    "PT",  # flake8-pytest-style
    "Q",   # flake8-quotes
    "RET", # flake8-return
    "SIM", # flake8-simplify
    "TCH", # flake8-type-checking
    "INT", # flake8-gettext
    "ARG", # flake8-unused-arguments
    "PGH", # pygrep-hooks
    "PL",  # pylint
    "TRY", # tryceratops
    "RUF", # ruff-specific rules
]

# Regras ignoradas
ignore = [
    "E501",    # line too long
    "PLR0913", # too many arguments
]

# Configurações específicas
[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"] # unused imports

[tool.ruff.isort]
known-first-party = ["backend_rag_ia"]
```

## Checklist de Verificação

Antes de considerar o código aprovado, verificar:

- [ ] Primeira execução do Ruff realizada
- [ ] Problemas encontrados foram corrigidos
- [ ] Segunda execução do Ruff realizada
- [ ] Nenhum novo problema encontrado
- [ ] Correções documentadas
- [ ] Código testado e funcionando
- [ ] Configuração do Ruff atualizada se necessário

## Exemplo de Documentação

```markdown
### Primeira Execução (DATA)

Problemas encontrados:

1. UP035: `typing.Tuple` é deprecated

   - Solução: Substituído por `tuple`

2. Q000: Aspas simples encontradas
   - Solução: Substituídas por aspas duplas

### Segunda Execução (DATA)

✅ Nenhum problema encontrado
```
