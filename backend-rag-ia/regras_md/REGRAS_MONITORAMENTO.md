# Regras de Monitoramento

## 1. Dashboard Render

### 1.1 Configurações Básicas

- Configurar notificações de status
- Habilitar alertas de falha
- Definir thresholds de performance
- Configurar webhooks para Slack

### 1.2 Métricas Importantes

- CPU e Memória
- Tempo de resposta
- Taxa de erros
- Número de requisições
- Status do healthcheck

## 2. Logs

### 2.1 Render Logs

- Acessar via dashboard
- Filtrar por severidade
- Buscar por palavras-chave
- Exportar logs para análise

### 2.2 Logs via SSH

```bash
# Logs em tempo real
ssh render tail -f /var/log/render/*.log

# Logs do deploy
ssh render cat /etc/render/deploy.log

# Logs do serviço
ssh render journalctl -u backend-rag-ia
```

## 3. Grafana/Loki

### 3.1 Configuração Local

```yaml
# /monitoring/docker-compose.yml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
```

### 3.2 Dashboards

- Overview do sistema
- Métricas de API
- Logs consolidados
- Alertas personalizados

## 4. Healthcheck

### 4.1 Endpoint

- Rota: `/api/v1/health`
- Método: GET
- Intervalo: 10 segundos
- Timeout: 30 segundos

### 4.2 Resposta

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "10d 2h 30m",
  "documents_count": 1000
}
```

## 5. Alertas

### 5.1 Configuração

- Slack para notificações
- Email para alertas críticos
- Webhook para integrações
- SMS para emergências

### 5.2 Tipos de Alerta

- Falha no healthcheck
- Alto uso de CPU/memória
- Erros 5xx frequentes
- Deploy falhou
- Reinício do serviço

## 6. SSH

### 6.1 Configuração

```bash
# ~/.ssh/config
Host render
    HostName ssh.oregon.render.com
    User srv-ctmtqra3esus739sknb0
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 6.2 Comandos de Monitoramento

```bash
# Status do serviço
ssh render systemctl status backend-rag-ia

# Uso de recursos
ssh render top
ssh render free -h
ssh render df -h

# Processos Python
ssh render ps aux | grep python

# Verificações
ssh render ls -la /app/
ssh render ls -la /opt/venv/
ssh render env | grep SUPABASE
```

## 7. Boas Práticas

### 7.1 Logs

- Usar níveis apropriados (INFO, ERROR, etc)
- Incluir contexto suficiente
- Rotacionar logs grandes
- Manter histórico adequado

### 7.2 Alertas

- Evitar falsos positivos
- Definir severidades claras
- Documentar procedimentos
- Manter contatos atualizados

### 7.3 Monitoramento

- Verificar regularmente
- Manter thresholds calibrados
- Documentar incidentes
- Fazer análise post-mortem
