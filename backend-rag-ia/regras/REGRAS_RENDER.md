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

## 3. Boas Práticas

- Usar multi-stage build no Dockerfile
- Manter dependências atualizadas no requirements.txt
- Configurar logs apropriadamente
- Documentar variáveis de ambiente necessárias
- Testar localmente antes do deploy

## 4. Monitoramento

### 4.1 Dashboard e Alertas

- Configurar notificações de status
- Monitorar logs através do dashboard
- Verificar métricas de performance
- Configurar alertas para falhas

### 4.2 Monitoramento via SSH

- Gerar chave SSH: `ssh-keygen -t ed25519 -C "seu-email@exemplo.com"`
- Adicionar chave pública no Render (Dashboard → Settings → SSH Keys)
- Testar conexão: `ssh <service>@ssh.render.com`

### 4.3 Comandos SSH Úteis

- Ver logs em tempo real: `ssh <service>@ssh.render.com tail -f /var/log/render/*.log`
- Status do serviço: `ssh <service>@ssh.render.com systemctl status <service>`
- Verificar deploy: `ssh <service>@ssh.render.com cat /etc/render/deploy.log`
- Monitorar recursos: `ssh <service>@ssh.render.com top`

### 4.4 Boas Práticas SSH

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
- Porta: 10000 (padrão do Render)
- Health Check: /api/v1/health
- Repositório: diegofornalha/backend-rag-ia

### 6.2 Configurações Técnicas

- Blueprint managed
- Internal Address: backend-rag-ia:10000
- Protocolo: HTTP
- Auto Deploy: Habilitado para branch main

**IMPORTANTE**: Este é o único serviço em produção até o momento. Não criar serviços adicionais sem autorização expressa.
