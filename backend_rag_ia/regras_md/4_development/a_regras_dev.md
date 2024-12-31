# Regras de Desenvolvimento

## 1. Padrões de Código

### 1.1 Estilo

- Seguir style guide da linguagem utilizada
- Manter consistência na formatação
- Utilizar ferramentas de lint
- Documentar código complexo

### 1.2 Nomenclatura

- Usar nomes descritivos e significativos
- Seguir convenções da linguagem
- Evitar abreviações não padrão
- Manter consistência nos termos

### 1.3 Organização

- Estruturar código em módulos coesos
- Separar responsabilidades
- Manter arquivos pequenos e focados
- Agrupar funcionalidades relacionadas

## 2. Qualidade de Código

### 2.1 Testes

- Escrever testes antes do código (TDD)
- Manter cobertura de testes adequada
- Testar casos de borda
- Implementar testes de integração

### 2.2 Performance

- Otimizar consultas ao banco de dados
- Implementar caching quando apropriado
- Monitorar uso de memória
- Realizar profiling quando necessário

### 2.3 Segurança

- Validar inputs adequadamente
- Implementar autenticação e autorização
- Proteger contra injeções
- Seguir princípios de OWASP

## 3. Versionamento

### 3.1 Git

- Fazer commits atômicos
- Escrever mensagens descritivas
- Manter histórico limpo
- Utilizar feature branches

### 3.2 Releases

- Seguir versionamento semântico
- Documentar mudanças no CHANGELOG
- Criar tags para releases
- Manter compatibilidade retroativa

## 4. Boas Práticas

### 4.1 Código Limpo

- Seguir princípios SOLID
- Evitar duplicação de código
- Manter métodos pequenos e focados
- Usar injeção de dependência

### 4.2 Documentação

- Manter README atualizado
- Documentar APIs
- Criar diagramas quando necessário
- Documentar decisões arquiteturais

## 1. Processamento de Documentos

### 1.1 Normalização de Conteúdo

- Todo conteúdo deve ser normalizado antes do processamento
- Remover BOM (Byte Order Mark) se presente
- Normalizar quebras de linha para LF
- Remover caracteres de controle, exceto newline
- Garantir codificação UTF-8 em todas as operações

### 1.2 Armazenamento

- Usar base64 para codificar conteúdo antes do armazenamento
- Manter hash SHA-256 do conteúdo normalizado
- Preservar metadados relevantes (nome, caminho, categoria)
- Incluir timestamp de atualização

### 1.3 Embeddings

- Gerar embeddings a partir do conteúdo original (não codificado)
- Usar modelo all-MiniLM-L6-v2 para embeddings
- Verificar existência de embeddings antes de criar novos
- Sincronizar embeddings após upload de documentos

## 2. Boas Práticas de Desenvolvimento

### 2.1 Tratamento de Erros

- Implementar tratamento adequado de exceções
- Fornecer feedback claro sobre erros
- Registrar falhas para análise posterior
- Permitir reprocessamento de documentos com falha

### 2.2 Performance

- Adicionar delays entre operações de upload
- Processar documentos em lotes quando possível
- Otimizar consultas ao banco de dados
- Cachear resultados quando apropriado

### 2.3 Segurança

- Validar entrada de dados
- Sanitizar conteúdo antes do processamento
- Usar conexões seguras com APIs
- Proteger credenciais e chaves de acesso
