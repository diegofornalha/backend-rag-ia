# Deploy no Render

Este documento descreve o processo de deploy da aplicação Flask no Render.

## Pré-requisitos

- Conta no Render (https://render.com)
- Git instalado localmente
- Render CLI instalado (`brew install render`)

## Configuração Inicial

1. Faça login no Render Dashboard
2. Crie um novo serviço estático
3. Conecte seu repositório GitHub

## Estrutura do render.yaml

```yaml
services:
  - type: static
    name: flask-frontend-static
    env: static
    buildCommand: pip install -r requirements_frontend.txt && python frontend/build.py
    staticPublishPath: frontend/static_build
    pullRequestPreviewsEnabled: true
    autoDeploy: false
    noHealthcheck: true
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

## Deploy Automatizado

O deploy é acionado automaticamente quando:

1. Há um push para a branch principal
2. Manualmente através do Dashboard
3. Via Render CLI

## Monitoramento

### Via Dashboard

1. Acesse o Render Dashboard
2. Selecione seu serviço
3. Vá para a aba "Logs"
4. Monitore o progresso do build e deploy

### Via CLI

```bash
# Instalar CLI
brew install render

# Login
render login

# Listar serviços
render list

# Ver logs
render logs <service-name>
```

## Configuração do Serviço

- **Build Command**: Comando para construir os arquivos estáticos
- **Publish Directory**: Diretório onde os arquivos estáticos são gerados
- **Auto-Deploy**: Desativado para maior controle
- **Health Checks**: Desativados para ambiente de teste

## Comandos Úteis

```bash
# Trigger manual deploy
render deploy <service-id>

# Ver status do serviço
render status <service-name>

# Ver variáveis de ambiente
render env list <service-name>
```

## Troubleshooting

### Problemas Comuns

1. **Build Falhou**

   - Verifique os logs do build
   - Confirme se todas as dependências estão no requirements.txt
   - Verifique se o buildCommand está correto

2. **Deploy Falhou**

   - Verifique se o staticPublishPath está correto
   - Confirme se os arquivos estáticos foram gerados corretamente

3. **Erro 404**
   - Verifique se as rotas estão configuradas corretamente
   - Confirme se o index.html existe no diretório de build

## API Keys e Autenticação

### Gerando API Key

1. Acesse o Render Dashboard
2. Vá para Account Settings > API Keys
3. Clique em "New API Key"
4. Copie e armazene a chave com segurança

### Usando API Key

```bash
# Configurar como variável de ambiente
export RENDER_API_KEY='seu_api_key'

# Testar autenticação
curl -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services
```

### Segurança

- Nunca compartilhe sua API Key
- Armazene em variáveis de ambiente
- Revogue imediatamente se comprometida

## One-Off Jobs

### Criando Jobs

```bash
# Via API
curl -X POST \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"startCommand": "python manage.py migrate"}' \
  https://api.render.com/v1/services/{service-id}/jobs
```

### Monitorando Jobs

1. Dashboard > Jobs
2. Ver status e logs
3. Histórico de execuções

## Suporte

Para problemas ou dúvidas:

1. Consulte a [documentação oficial do Render](https://render.com/docs)
2. Abra um ticket de suporte no Dashboard
3. Consulte os logs detalhados do serviço
