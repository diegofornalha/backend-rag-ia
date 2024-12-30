# Regras do Projeto

## Gerenciamento de Regras

### Organização das Regras

1. **Localização das Regras**:

   - Todas as regras devem estar na pasta `backend_rag_ia/regras_md/`
   - Não criar novas pastas para regras
   - Não duplicar pastas de regras

2. **Adicionando Novas Regras**:

   - Quando receber instrução para "colocar" regras:
     - Adicionar no arquivo `.md` correspondente em `regras_md/`
     - Não criar nova pasta, usar a estrutura existente
   - Para temas completamente novos:
     - Criar novo arquivo `.md` dentro de `regras_md/`
     - Seguir padrão de nomenclatura: `REGRAS_NOVO_TEMA.md`

3. **Estrutura de Arquivos**:
   ```
   backend_rag_ia/
   └── regras_md/
       ├── PROJECT_RULES.md
       ├── REGRAS_API.md
       ├── REGRAS_DOCKER.md
       ├── REGRAS_RENDER.md
       └── ... (outros arquivos de regras)
   ```

### Boas Práticas

1. **Manutenção**:

   - Manter regras organizadas por tema
   - Atualizar arquivos existentes ao invés de criar novos
   - Evitar duplicação de informações

2. **Nomenclatura**:

   - Usar MAIÚSCULAS para nomes de arquivos
   - Prefixo "REGRAS\_" para arquivos de regras
   - Sufixo ".md" para todos os arquivos

3. **Conteúdo**:
   - Manter formatação Markdown consistente
   - Organizar regras hierarquicamente
   - Incluir exemplos quando necessário

## 1. Estrutura de Diretórios

### 1.1 Arquivos na Raiz

- **Dockerfile** → Build da aplicação
- **requirements.txt** → Dependências Python
- **render.yaml** → Configurações do Render (opcional)

### 1.2 Organização de Pastas

- **/regras** → Documentação e regras do projeto
- **/monitoring** → Configurações de monitoramento
- **/api** → Código da API
- **/services** → Serviços da aplicação
- **/scripts** → Scripts utilitários

## 2. Padrões de Código

### 2.1 Python

- Usar Python 3.11+
- Seguir PEP 8
- Documentar funções e classes
- Usar type hints

### 2.2 Docker

- Multi-stage builds
- Imagens slim
- Limpar caches
- Healthchecks configurados

### 2.3 API

- Endpoints versionados
- Documentação Swagger
- Validação de dados
- Tratamento de erros

## 3. Ambiente de Desenvolvimento

### 3.1 Dependências

- Manter requirements.txt atualizado
- Usar versões específicas
- Documentar dependências opcionais
- Separar dev e prod requirements

### 3.2 Variáveis de Ambiente

- Usar .env para desenvolvimento
- Nunca commitar .env
- Documentar todas as variáveis
- Usar defaults seguros

## 4. Deploy e Monitoramento

### 4.1 Render

- HOST = "0.0.0.0"
- PORT = 10000
- Healthcheck a cada 10s
- Logs configurados

### 4.2 Monitoramento

- Grafana para métricas
- Loki para logs
- Alertas configurados
- Dashboards documentados

## 4. Regras de Upload para Supabase

4.1 Formato de Upload:

- **APENAS** arquivos `.json` devem ser enviados ao Supabase
- Arquivos `.md` são usados somente para edição/criação
- Sempre converter `.md` para `.json` antes do upload

  4.2 Fluxo de Trabalho:

```bash
1. Criar/Editar regras em formato .md
2. Converter .md para .json usando o script de conversão
3. Fazer upload APENAS dos arquivos .json para o Supabase
```

4.3 Justificativa:

- Evita duplicidade de dados no Supabase
- Mantém consistência no formato dos documentos
- Garante estrutura padronizada dos dados
- Previne inconsistências entre versões

## 5. Segurança

### 5.1 Código

- Não expor secrets
- Validar inputs
- Sanitizar outputs
- Manter dependências seguras

### 5.2 Infraestrutura

- CORS configurado
- Rate limiting
- Autenticação/Autorização
- Backups automáticos
