# Deploy no Render

Este documento descreve o processo de deploy da aplicação no Render.

## Pré-requisitos

1. Ter o Render CLI instalado:

```bash
# Para MacOS
brew update
brew install render

# Para Linux
curl -L https://github.com/render-oss/cli/releases/download/v1.1.0/cli_1.1.0_linux_amd64.zip -o render.zip
unzip render.zip
sudo mv cli_v1.1.0 /usr/local/bin/render
```

2. Ter uma conta no Render (dashboard.render.com)

## CI/CD com GitHub Actions

O projeto já possui integração contínua configurada através do GitHub Actions (`.github/workflows/docker-publish.yml`):

1. **Triggers**:

   - Push na branch `main`
   - Pull Requests para `main`

2. **Ações Automatizadas**:

   - Build da imagem Docker
   - Push para GitHub Container Registry
   - Tags automáticas baseadas em:
     - Branch
     - Pull Request
     - Versão semântica
     - SHA do commit

3. **Workflow**:

```yaml
name: Docker Build and Push
on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
```

## Configuração Inicial

1. **Login no Render CLI**:

```bash
render login
```

Siga as instruções no navegador para autorizar o CLI.

2. **Configurar o Workspace**:

```bash
# Liste os workspaces disponíveis
render workspace list

# Configure o workspace (substitua WORKSPACE_ID pelo seu ID)
render workspace set WORKSPACE_ID
```

Nosso Workspace ID: `tea-ctm6tfdumphs73ddibgg`

## Deploy Automatizado

1. **Obter o SERVICE_ID**:

```bash
render services --output json
```

Nosso SERVICE_ID: `srv-ctocnotds78s73cbfuhg`

2. **Configurar Variável de Ambiente**:

```bash
export RENDER_SERVICE_ID=srv-ctocnotds78s73cbfuhg
```

3. **Executar o Deploy**:

```bash
./deploy.sh
```

O script `deploy.sh` automatiza:

- Commit das alterações
- Push para o GitHub
- Deploy no Render

## Fluxo de Deploy

1. **Desenvolvimento Local**:

   - Faça suas alterações
   - Teste localmente
   - Commit e push

2. **CI/CD Automático**:

   - GitHub Actions constrói a imagem Docker
   - Push para o Container Registry
   - Render detecta a nova imagem

3. **Deploy no Render**:
   - Manual via CLI: `./deploy.sh`
   - Automático após CI: Configurado no `render.yaml`

## Monitoramento

1. **Ver Status do Deploy**:

```bash
render deploys list $RENDER_SERVICE_ID --output json
```

2. **Logs em Tempo Real**:

```bash
render logs $RENDER_SERVICE_ID
```

3. **Status do Serviço**:

```bash
render service get $RENDER_SERVICE_ID --output json
```

## Configuração do Serviço

O arquivo `render.yaml` define a configuração do serviço:

```yaml
services:
  - type: static
    name: flask-frontend-static
    env: static
    buildCommand: pip install -r requirements_frontend.txt && python frontend/build.py
    staticPublishPath: frontend/static_build
    pullRequestPreviewsEnabled: true
    autoDeploy: false
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

## Comandos Úteis

1. **Criar Novo Deploy**:

```bash
render deploys create $RENDER_SERVICE_ID --output json --confirm
```

2. **Listar Todos os Serviços**:

```bash
render services --output json
```

3. **Verificar Logs de um Deploy Específico**:

```bash
render deploys logs $DEPLOY_ID
```

## Troubleshooting

1. **Erro de Autenticação**:

```bash
render login  # Faça login novamente
```

2. **Workspace não Configurado**:

```bash
render workspace set tea-ctm6tfdumphs73ddibgg
```

3. **Deploy Falhou**:

```bash
render deploys logs $(render deploys list $RENDER_SERVICE_ID --output json | jq -r '.[0].id')
```

4. **Problemas com CI/CD**:
   - Verifique as Actions no GitHub
   - Confirme as permissões do token
   - Verifique os logs do Container Registry

## Links Úteis

- [Dashboard do Render](https://dashboard.render.com)
- [Documentação do Render CLI](https://render.com/docs/cli)
- [Configuração do render.yaml](https://render.com/docs/yaml-spec)
- [GitHub Actions](https://github.com/features/actions)
- [Container Registry](https://github.com/features/packages)

## Autenticação com API Key

⚠️ **IMPORTANTE: Nunca compartilhe ou exponha sua API Key!**

1. **Gerar API Key**:

   - Acesse [Account Settings no Render Dashboard](https://dashboard.render.com/account/settings)
   - Procure a seção "API Keys"
   - Clique em "Create API Key"

2. **Configurar API Key**:

```bash
# Configurar como variável de ambiente
export RENDER_API_KEY=rnd_YOUR_API_KEY_HERE

# Ou adicionar ao .env (não commitar este arquivo!)
echo "RENDER_API_KEY=rnd_YOUR_API_KEY_HERE" >> .env
```

3. **Testar API Key**:

```bash
# Teste básico com curl
curl --request GET \
     --url 'https://api.render.com/v1/services?limit=3' \
     --header 'Accept: application/json' \
     --header 'Authorization: Bearer $RENDER_API_KEY'

# Ou usando o Render CLI
render services --output json
```

4. **Segurança**:
   - Nunca compartilhe sua API Key
   - Não commite no controle de versão
   - Revogue imediatamente se comprometida
   - Use variáveis de ambiente em CI/CD
