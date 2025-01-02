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


## Decisão: Configuração CORS da API

- Tipo: tecnico
- Contexto: Discutir a melhor abordagem para configuração CORS da API, considerando segurança, flexibilidade e manutenibilidade
- Data Início: 2025-01-02 01:59:03.695901
- Data Resolução: 2025-01-02T01:59:25.634524

### Argumentos:

- **AI** (tecnico): A solução atual de usar CORS_ORIGINS_LIST=['*'] não é a melhor prática pois: 1) Permite acesso de qualquer origem sem restrições, 2) Não diferencia ambientes (dev/prod), 3) Não segue princípios de segurança Zero Trust
- **AI** (tecnico): Uma abordagem mais segura seria: 1) Definir origens específicas por ambiente no .env, 2) Implementar uma lista branca de domínios permitidos, 3) Adicionar validação de origem nas requisições

### Decisão Final
Implementar configuração CORS baseada em ambiente com lista branca de origens

### Razão
A solução atual de permitir todas as origens (*) é insegura e não segue boas práticas. Devemos implementar uma configuração mais restritiva que: 1) Use variáveis de ambiente para definir origens permitidas por ambiente, 2) Implemente uma lista branca de domínios confiáveis, 3) Adicione validação de origem nas requisições. Isso melhora a segurança sem comprometer a funcionalidade.


## Decisão: Estrutura de Testes para Sistema de Embates

- Tipo: tecnico
- Contexto: Definir a melhor estrutura e abordagem para implementação dos testes unitários e de integração do sistema de embates, considerando cobertura, manutenibilidade e confiabilidade
- Data Início: 2025-01-02 02:01:53.612152
- Data Resolução: 2025-01-02T02:02:26.721150

### Argumentos:

- **AI** (tecnico): Para os testes unitários, proponho a seguinte estrutura em 06_testes_apenas_raiz/1_unit/: 1) test_condensador.py para testar cada método da classe CondensadorEmbates isoladamente com mocks, 2) test_similarity.py para testar funções de similaridade com casos conhecidos, 3) test_schemas.py para validar os schemas Pydantic com casos válidos e inválidos
- **AI** (tecnico): Para os testes de integração em 06_testes_apenas_raiz/2_integration/: 1) test_embates_flow.py para testar o fluxo completo de criar, adicionar argumentos e resolver embates, 2) test_supabase_sync.py para testar a sincronização com Supabase usando mocks, 3) test_rules_generation.py para validar a geração e formatação das regras MD
- **AI** (tecnico): Para fixtures e utilidades em 06_testes_apenas_raiz/4_fixtures/ e 5_utils/: 1) conftest.py com fixtures compartilhadas como mock_supabase e sample_embates, 2) test_utils.py com funções auxiliares para criar dados de teste, 3) test_data/ com arquivos JSON e MD de exemplo para testes

### Decisão Final
Implementar estrutura completa de testes seguindo as divisões propostas

### Razão
A estrutura proposta oferece uma cobertura completa e organizada dos testes, separando claramente testes unitários, de integração e fixtures. A divisão em arquivos específicos facilita a manutenção e compreensão, enquanto as fixtures compartilhadas reduzem duplicação de código. Esta abordagem permite testar todos os aspectos críticos do sistema de embates de forma isolada e integrada.
