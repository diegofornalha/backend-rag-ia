# Regras de Verificação Dupla

## 1. Princípios

- **Sempre** realizar duas verificações independentes
- **Nunca** assumir sucesso sem segunda verificação
- **Documentar** todo o processo detalhadamente
- **Validar** codificação UTF-8 dos arquivos

## 2. Processo de Verificação

### Primeira Verificação

1. **Busca Inicial**:

   ```bash
   # Verificar codificação do arquivo
   file -I arquivo.md

   # Busca com grep considerando codificação
   LC_ALL=C grep -r "termo_busca" ./
   ```

2. **Documentação**:

   ```markdown
   ### Verificação de [FEATURE] - [DATA]

   1. Primeira Verificação:
      - Codificação: UTF-8
      - Método: grep com LC_ALL=C
      - Arquivos: [lista]
      - Caracteres especiais: [detalhes]
   ```

### Segunda Verificação

1. **Método Diferente**:

   ```bash
   # Verificar e converter quebras de linha
   dos2unix arquivo.md

   # Busca com find e validação de codificação
   find . -type f -exec sh -c 'file -i "{}" | grep -q "utf-8" && grep -l "termo_busca" "{}"' \;
   ```

2. **Documentação**:
   ```markdown
   2. Segunda Verificação:
      - Normalização: LF (Unix)
      - Método: find + grep com validação UTF-8
      - Resultado: [detalhes]
      - Status: ✅ Validado
   ```

## 3. Critérios de Conclusão

✅ **Concluído quando**:

- Duas verificações sem encontrar referências
- Codificação UTF-8 confirmada
- Quebras de linha normalizadas
- Testes passando
- Documentação completa
- Evidências arquivadas

❌ **Não concluído se**:

- Apenas uma verificação realizada
- Problemas de codificação detectados
- Documentação incompleta
- Dúvidas pendentes
- Testes falhando

## 4. Exemplo Completo
