# Estrutura das Tabelas

## Schema `public`

Este schema contém as tabelas e funções principais do sistema RAG.

### Tabela `base_conhecimento_regras_geral`

Tabela principal que armazena os documentos e seus embeddings.

Colunas:

- `id`: UUID - Identificador único do documento
- `titulo`: TEXT - Título do documento
- `conteudo`: TEXT - Conteúdo do documento
- `embedding`: vector - Vetor de embedding do documento
- `metadata`: jsonb - Metadados adicionais do documento
- `created_at`: TIMESTAMP - Data de criação
- `updated_at`: TIMESTAMP - Data da última atualização
- `owner_id`: UUID - ID do usuário dono do documento
- `document_hash`: TEXT - Hash do documento para controle de duplicidade

### Políticas de Segurança (RLS)

- `select_knowledge`: Permite leitura de documentos públicos ou próprios
- `insert_knowledge`: Permite inserção apenas para usuários autenticados
- `update_knowledge`: Permite atualização apenas pelo dono do documento
- `delete_knowledge`: Permite deleção apenas pelo dono do documento

### Funções

- `generate_embedding(text)`: Gera embedding para um texto
- `match_documents(vector, float, integer)`: Busca documentos similares

## Observações

1. Todas as tabelas têm RLS habilitado para segurança
2. Os nomes das colunas estão em português para consistência
3. A tabela foi renomeada de `knowledge_base` para `base_conhecimento_regras_geral`
4. O document_hash garante unicidade do conteúdo
