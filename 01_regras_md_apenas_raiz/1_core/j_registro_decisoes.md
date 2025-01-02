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


## Decisão: Teste CLI

- Tipo: tecnico
- Contexto: Testando comandos CLI
- Data Início: 2025-01-02 01:41:34.869396
- Data Resolução: 2025-01-02T01:42:35.987376

### Argumentos:

- **AI** (tecnico): Este é um argumento de teste

### Decisão Final
Decisão de teste

### Razão
Razão de teste


## Decisão: Localização do Diretório de Embates

- Tipo: tecnico
- Contexto: Decidir o melhor lugar para armazenar os arquivos de embates, considerando a estrutura do projeto e as responsabilidades de cada diretório
- Data Início: 2025-01-02 01:44:48.145757
- Data Resolução: 2025-01-02T01:45:20.925299

### Argumentos:

- **AI** (tecnico): O diretório 'dados/' na raiz não é a melhor localização pois: 1) Mistura dados de runtime com código fonte, 2) Não segue o padrão de nomenclatura _apenas_raiz dos outros diretórios, 3) Pode causar confusão com outros tipos de dados do sistema
- **AI** (tecnico): O diretório '02_ferramentas_rag_apenas_raiz' seria uma localização mais apropriada pois: 1) Os embates são uma ferramenta do RAG, 2) Segue o padrão de nomenclatura _apenas_raiz, 3) Mantém a organização lógica do projeto
- **AI** (tecnico): Especificamente, sugiro mover para '02_ferramentas_rag_apenas_raiz/dados_embates/' para: 1) Manter os dados próximos da ferramenta que os utiliza, 2) Separar claramente que são dados específicos dos embates, 3) Facilitar o backup e versionamento junto com o código

### Decisão Final
Mover o diretório de embates para '02_ferramentas_rag_apenas_raiz/dados_embates/'

### Razão
A nova localização é mais apropriada pois mantém os dados próximos da ferramenta que os utiliza, segue o padrão de nomenclatura do projeto, facilita o versionamento e evita confusão com outros tipos de dados. Além disso, a mudança melhora a organização lógica do projeto ao agrupar funcionalidades relacionadas.
