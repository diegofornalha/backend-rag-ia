# Regras do Supabase

## 1. Formato de Documentos

### 1.1 Tipos de Arquivos

- **APENAS** arquivos `.json` devem ser enviados ao Supabase
- Arquivos `.md` são usados somente para edição/criação
- Sempre converter `.md` para `.json` antes do upload

### 1.2 Fluxo de Trabalho

```bash
1. Criar/Editar regras em formato .md
2. Converter .md para .json usando o script de conversão
3. Fazer upload APENAS dos arquivos .json para o Supabase
```

### 1.3 Justificativa

- Evita duplicidade de dados no Supabase
- Mantém consistência no formato dos documentos
- Garante estrutura padronizada dos dados
- Previne inconsistências entre versões

## 2. Embeddings

### 2.1 Gerenciamento

- Sempre gerar embeddings junto com o upload
- Verificar se documento foi vinculado corretamente ao embedding
- Aguardar confirmação de sucesso antes de prosseguir
- Manter logs de falhas de upload
- Manter backup dos embeddings

### 2.2 Verificações

- Verificar hash antes de cada upload para evitar duplicatas
- Verificar integridade dos embeddings periodicamente
- Limpar documentos órfãos (sem embedding)
- Manter índices otimizados

## 3. Buscas e Consultas

### 3.1 Configurações

- Usar match threshold adequado nas buscas semânticas
- Implementar fallback para buscas que não retornam resultados
- Limitar número de resultados para otimizar performance
- Cachear resultados frequentes

### 3.2 Performance

- Monitorar uso de storage
- Manter índices otimizados
- Implementar estratégias de cache
- Monitorar tempo de resposta das queries

## 4. Segurança

### 4.1 Credenciais

- Nunca expor chaves de API
- Usar apenas conexões seguras
- Manter políticas RLS atualizadas
- Rotacionar credenciais periodicamente

### 4.2 Políticas

- Configurar RLS (Row Level Security) adequadamente
- Nunca exceder limite de RLS
- Revisar políticas periodicamente
- Documentar todas as políticas implementadas
