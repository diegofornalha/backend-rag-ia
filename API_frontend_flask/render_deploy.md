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

## Links Úteis

- [Dashboard do Render](https://dashboard.render.com)
- [Documentação do Render CLI](https://render.com/docs/cli)
- [Configuração do render.yaml](https://render.com/docs/yaml-spec)
