# Regras do Render

## 1. Estrutura de Arquivos

### 1.1 Arquivos Obrigatórios na Raiz

- **Dockerfile** → Arquivo principal para build da aplicação
- **requirements.txt** → Dependências Python do projeto
- **render.yaml** → Configurações de infraestrutura (opcional)

### 1.2 Variáveis de Ambiente

- Configurar na plataforma do Render
- Não expor valores sensíveis no código
- HOST deve ser configurado como "0.0.0.0"
- PORT deve ser 10000 (padrão do Render)

## 2. Deploy

### 2.1 Detecção Automática

- O Render detecta automaticamente o Dockerfile na raiz
- Não é necessário configurar comandos de build/start manualmente
- O healthcheck é importante para o Render monitorar a aplicação

### 2.2 Healthcheck

- Endpoint `/api/v1/health` é obrigatório
- O Render verifica a cada 10 segundos
- Timeout de 30 segundos para resposta
- Falhas múltiplas podem causar redeploy

## 3. Monitoramento no Render

### 3.1 Dashboard

- Configurar notificações de status
- Habilitar alertas de falha
- Definir thresholds de performance
- Configurar webhooks para Slack

### 3.2 Métricas

- CPU e Memória
- Tempo de resposta
- Taxa de erros
- Número de requisições
- Status do healthcheck

### 3.3 Logs do Render

- Acessar via dashboard
- Filtrar por severidade
- Buscar por palavras-chave
- Exportar logs para análise

## 4. Acesso SSH

### 4.1 Configuração SSH

```bash
# ~/.ssh/config
Host render
    HostName ssh.oregon.render.com
    User srv-ctmtqra3esus739sknb0
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 4.2 Comandos SSH Úteis

```bash
# Logs em tempo real
ssh render tail -f /var/log/render/*.log

# Status do serviço
ssh render systemctl status backend-rag-ia

# Logs do deploy
ssh render cat /etc/render/deploy.log

# Verificar recursos
ssh render top
ssh render free -h
ssh render df -h

# Verificar arquivos
ssh render ls -la /app/
ssh render ls -la /opt/venv/
```

### 4.3 Boas Práticas SSH

- Manter chaves SSH seguras
- Usar nomes descritivos para as chaves
- Revogar acesso de chaves não utilizadas
- Monitorar tentativas de acesso suspeitas

## 5. Segurança

- Não commitar arquivos .env
- Usar variáveis de ambiente do Render
- Manter secrets seguros
- Seguir práticas de segurança do Docker

## 6. Informações do Serviço

### 6.1 Configurações Gerais

- Nome: coflow
- URL: api.coflow.com.br
- Tipo: Docker (Standard)
- Branch: main
- Região: Oregon
- Porta: 10000
- Health Check: /api/v1/health
- Repositório: diegofornalha/backend-rag-ia

### 6.2 Configurações Técnicas

- Blueprint managed
- Internal Address: backend-rag-ia:10000
- Protocolo: HTTP
- Auto Deploy: Habilitado para branch main

**IMPORTANTE**: Este é o único serviço em produção até o momento. Não criar serviços adicionais sem autorização expressa.
