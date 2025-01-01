# Registro de Decisões

## Decisão: Padronização de Nomenclatura de Diretórios Raiz

- Data: 2024-02-14
- Conflito: Nomenclatura de diretórios raiz entre padrão existente e novo padrão numérico
- Resolução: Adotar padrão `NN_nome_apenas_raiz` para todos os diretórios raiz, exceto `backend_rag_ia`
- Razão: Melhor organização, facilidade de ordenação e clareza na estrutura do projeto
- Aprovação: Automática (boa prática > preferência pessoal)
- Impacto: Renomeação de todos os diretórios raiz para seguir o novo padrão

### Detalhes da Implementação

1. Novo Padrão:

   ```
   /
   ├── backend_rag_ia/          # Exceção (core)
   ├── 01_regras_md_apenas_raiz/
   ├── 02_logs_apenas_raiz/
   ├── 03_monitoring_apenas_raiz/
   ├── 04_scripts_apenas_raiz/
   ├── 05_sql_apenas_raiz/
   └── 06_testes_apenas_raiz/
   ```

2. Justificativa da Exceção:

   - `backend_rag_ia` mantido sem numeração por ser o core da aplicação
   - Convenção estabelecida e amplamente utilizada no projeto
   - Clareza na identificação do componente principal

3. Benefícios:

   - Ordenação clara e consistente
   - Fácil identificação de componentes
   - Melhor organização visual
   - Padronização da estrutura

4. Documentação Atualizada:
   - Regras de nomenclatura atualizadas
   - Exemplos adicionados
   - Referências cruzadas estabelecidas
