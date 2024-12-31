# Regras de Monitoramento

## 1. Métricas Importantes

### 1.1 Performance

- CPU e Memória
- Tempo de resposta
- Taxa de erros
- Número de requisições
- Status do healthcheck

### 1.2 Configurações Básicas

- Configurar notificações de status
- Habilitar alertas de falha
- Definir thresholds de performance
- Configurar webhooks para integrações

## 2. Grafana/Loki

### 2.1 Configuração Local

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

### 2.2 Dashboards

- Overview do sistema
- Métricas de API
- Logs consolidados
- Alertas personalizados

## 3. Healthcheck

### 3.1 Endpoint

- Rota: `/api/v1/health`
- Método: GET
- Intervalo: 10 segundos
- Timeout: 30 segundos

### 3.2 Resposta

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": "10d 2h 30m",
  "documents_count": 1000
}
```

## 4. Alertas

### 4.1 Configuração

- Slack para notificações
- Email para alertas críticos
- Webhook para integrações
- SMS para emergências

### 4.2 Tipos de Alerta

- Falha no healthcheck
- Alto uso de CPU/memória
- Erros 5xx frequentes
- Deploy falhou
- Reinício do serviço

## 5. Boas Práticas

### 5.1 Monitoramento

- Verificar regularmente
- Manter thresholds calibrados
- Documentar incidentes
- Fazer análise post-mortem

### 5.2 Alertas

- Evitar falsos positivos
- Definir severidades claras
- Documentar procedimentos
- Manter contatos atualizados
