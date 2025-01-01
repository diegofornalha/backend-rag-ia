# Regras do Supabase

## 1. Diretriz Principal: Consultar Antes de Criar

### 1.1 Processo de Consulta

1. **Verificar Base Existente**:

   - Buscar documentos similares na base
   - Verificar possibilidade de atualização
   - Analisar duplicidade de conteúdo
   - Consultar histórico de versões

2. **Antes de Inserir**:

   - Verificar hash do documento
   - Buscar conteúdo similar
   - Considerar atualização vs inserção
   - Documentar decisão de criar novo

3. **Gestão de Recursos**:
   - Priorizar atualização sobre criação
   - Manter base de conhecimento enxuta
   - Evitar fragmentação de informação
   - Consolidar conteúdos relacionados

### 1.2 Identificação de Documentos

1. **Regras de Identificação**:

   - Documento NOVO: não existe `file_path` correspondente no metadata
   - Documento ATUALIZADO: existe `file_path` mas hash é diferente
   - Documento EXISTENTE: existe `file_path` e hash é igual

2. **Processo de Verificação**:

   - Primeiro verifica o `file_path` no metadata
   - Se encontrar, compara o hash do conteúdo
   - Se hash diferente, atualiza documento e embeddings
   - Se hash igual, mantém documento sem alterações

3. **Justificativa**:
   - Evita duplicação de documentos
   - Mantém histórico de alterações
   - Garante consistência dos dados
   - Otimiza processo de sincronização

## 2. Formato de Documentos

### 2.1 Tipos de Arquivos

- **APENAS** arquivos `.json` devem ser enviados ao Supabase
- Arquivos `.md` são usados somente para edição/criação
- Sempre converter `.md` para `.json` antes do upload

### 2.2 Fluxo de Trabalho

```bash
1. Criar/Editar regras em formato .md
2. Converter .md para .json usando o script de conversão
3. Fazer upload APENAS dos arquivos .json para o Supabase
```

### 2.3 Justificativa

- Evita duplicidade de dados no Supabase
- Mantém consistência no formato dos documentos
- Garante estrutura padronizada dos dados
- Previne inconsistências entre versões

## 3. Estrutura de Tabelas

### 3.1 Separação de Responsabilidades

1. **Tabela `01_base_conhecimento_regras_geral`**:

   - Armazena documentos e metadados
   - Mantém controle de versão
   - Gerencia permissões de acesso
   - Controla duplicidade via hash

2. **Tabela `02_embeddings_regras_geral`**:
   - Armazena vetores de embedding
   - Otimizada para buscas semânticas
   - Mantém referência ao documento original
   - Permite regeneração independente

### 3.2 Justificativa da Separação

1. **Performance**:

   - Índices específicos para cada tipo de busca
   - Otimização de cache independente
   - Queries mais eficientes

2. **Manutenção**:

   - Atualização de embeddings sem afetar documentos
   - Regeneração em lote quando necessário
   - Backup seletivo de cada tipo de dado

3. **Escalabilidade**:
   - Crescimento independente das tabelas
   - Distribuição de carga
   - Melhor gerenciamento de recursos

### 3.3 Estrutura das Tabelas

1. **01_base_conhecimento_regras_geral**:

   - `id`: UUID (PK)
   - `titulo`: TEXT
   - `conteudo`: TEXT
   - `metadata`: jsonb
   - `created_at`: TIMESTAMP
   - `updated_at`: TIMESTAMP
   - `owner_id`: UUID
   - `document_hash`: TEXT

2. **02_embeddings_regras_geral**:
   - `id`: UUID (PK)
   - `documento_id`: UUID (FK)
   - `embedding`: vector
   - `modelo`: TEXT
   - `created_at`: TIMESTAMP
   - `updated_at`: TIMESTAMP
   - `metadata`: jsonb

### 3.4 Convenção de Nomenclatura

1. **Prefixos Numéricos**:

   - Prefixo `01_` para tabela principal de documentos
   - Prefixo `02_` para tabela de embeddings
   - Facilita ordenação e visualização
   - Indica dependências entre tabelas

2. **Sufixo `_geral`**:
   - Indica escopo global das tabelas
   - Diferencia de possíveis tabelas específicas futuras
   - Mantém consistência na nomenclatura

## 4. Buscas e Consultas

### 4.1 Configurações

- Usar match threshold adequado nas buscas semânticas
- Implementar fallback para buscas que não retornam resultados
- Limitar número de resultados para otimizar performance
- Cachear resultados frequentes

### 4.2 Performance

- Monitorar uso de storage
- Manter índices otimizados
- Implementar estratégias de cache
- Monitorar tempo de resposta das queries

## 5. Segurança

### 5.1 Credenciais

- Nunca expor chaves de API
- Usar apenas conexões seguras
- Manter políticas RLS atualizadas
- Rotacionar credenciais periodicamente

### 5.2 Políticas RLS

- Configurar RLS adequadamente
- Nunca exceder limite de RLS
- Revisar políticas periodicamente
- Documentar todas as políticas implementadas

## 6. Manutenção

### 6.1 Limpeza

- Remover documentos obsoletos
- Limpar embeddings órfãos
- Manter índices otimizados
- Monitorar uso de espaço

### 6.2 Backup

- Backup diário dos documentos
- Backup semanal completo
- Testar restauração periodicamente
- Manter logs de backup

### 6.3 Gestão de Conteúdo

- Revisar documentos periodicamente
- Consolidar informações similares
- Atualizar conteúdo existente
- Evitar fragmentação de conhecimento
