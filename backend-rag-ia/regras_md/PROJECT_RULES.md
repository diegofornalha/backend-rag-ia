# Regras do Projeto

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
