# Regras de Verificação Dupla

## 1. Princípios

- **Sempre** realizar duas verificações independentes
- **Nunca** assumir sucesso sem segunda verificação
- **Documentar** todo o processo

## 2. Processo de Verificação

### Primeira Verificação

1. **Busca Inicial**:

   ```bash
   # Exemplo com grep
   grep -r "termo_busca" ./
   ```

2. **Documentação**:

   ```markdown
   ### Remoção de [FEATURE] - [DATA]

   1. Primeira Verificação:
      - Método: grep case-insensitive
      - Arquivos: [lista]
      - Alterações: [detalhes]
   ```

### Segunda Verificação

1. **Método Diferente**:

   ```bash
   # Exemplo com find
   find . -type f -exec grep -l "termo_busca" {} \;
   ```

2. **Documentação**:
   ```markdown
   2. Segunda Verificação:
      - Método: find + grep
      - Resultado: [detalhes]
      - Status: ✅ Concluído
   ```

## 3. Critérios de Conclusão

✅ **Concluído quando**:

- Duas verificações sem encontrar referências
- Testes passando
- Documentação completa
- Evidências arquivadas

❌ **Não concluído se**:

- Apenas uma verificação realizada
- Documentação incompleta
- Dúvidas pendentes
- Testes falhando

## 4. Exemplo Completo

```markdown
### Remoção de Express.js (2023-12-31)

1. Primeira Verificação:

   - Método: grep case-insensitive
   - Comando: grep -ri "express" ./
   - Arquivos encontrados:
     - docs/RULES.md
     - requirements.txt
   - Alterações: Removidas todas referências

2. Segunda Verificação:
   - Método: find + grep
   - Comando: find . -type f -exec grep -l "express" {} \;
   - Resultado: Nenhuma referência encontrada
   - Testes: ✅ Passando

✅ Conclusão: Remoção completa confirmada
📝 Documentação atualizada
🧪 Testes validados
```
