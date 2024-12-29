# Regras de Logs

## 1. Estrutura de Logs

### 1.1 Níveis de Log

- ERROR: Erros que precisam de atenção imediata
- WARNING: Situações problemáticas mas não críticas
- INFO: Informações gerais do sistema
- DEBUG: Detalhes para desenvolvimento

### 1.2 Formato Padrão

```python
{
    "timestamp": "2024-01-01T10:00:00Z",
    "level": "INFO",
    "service": "backend-rag-ia",
    "endpoint": "/api/v1/documents",
    "message": "Processando documento",
    "details": {...},
    "trace_id": "uuid4"
}
```

## 2. Fontes de Log

### 2.1 Logs da Aplicação

- Diretório: `/app/logs/`
- Rotação: Diária
- Retenção: 30 dias
- Formato: JSON

### 2.2 Logs do Render

- Dashboard do Render
- Logs do deploy
- Logs do sistema
- Métricas de performance

### 2.3 Logs do Sistema

- Logs do Python/Uvicorn
- Logs do Docker
- Logs do Sistema Operacional
- Logs de Segurança

## 3. Coleta e Armazenamento

### 3.1 Loki

```yaml
# Configuração do Loki
auth_enabled: false
server:
  http_listen_port: 3100
schema_config:
  configs:
    - from: 2020-05-15
      store: boltdb
      object_store: filesystem
      schema: v11
```

### 3.2 Retenção

- Logs de aplicação: 30 dias
- Logs de erro: 90 dias
- Logs de auditoria: 1 ano
- Logs de deploy: 60 dias

## 4. Consulta de Logs

### 4.1 Via SSH

```bash
# Logs da aplicação
ssh render tail -f /app/logs/app.log

# Logs do sistema
ssh render journalctl -u backend-rag-ia

# Logs do deploy
ssh render cat /etc/render/deploy.log

# Logs específicos
ssh render grep ERROR /app/logs/app.log
```

### 4.2 Via Grafana

- Queries LogQL
- Dashboards personalizados
- Alertas baseados em logs
- Visualizações temporais

## 5. Boas Práticas

### 5.1 Logging

- Usar logging estruturado (JSON)
- Incluir trace_id em todas as requisições
- Evitar informações sensíveis
- Manter contexto adequado

### 5.2 Performance

- Usar log levels apropriadamente
- Implementar log buffering
- Configurar rotação de logs
- Monitorar espaço em disco

### 5.3 Segurança

- Sanitizar dados sensíveis
- Implementar rate limiting
- Proteger arquivos de log
- Manter backups seguros

## 6. Troubleshooting

### 6.1 Comandos Úteis

```bash
# Buscar erros recentes
ssh render grep -r "ERROR" /app/logs/

# Contar ocorrências
ssh render awk '/ERROR/ {print $0}' /app/logs/app.log | wc -l

# Análise temporal
ssh render sed -n '/2024-01-01/,/2024-01-02/p' /app/logs/app.log

# Logs específicos
ssh render find /app/logs/ -name "*.log" -mtime -7
```

### 6.2 Análise de Problemas

- Verificar logs em ordem cronológica
- Correlacionar eventos entre serviços
- Identificar padrões de erro
- Documentar soluções encontradas

## 7. Monitoramento de Logs

### 7.1 Alertas

- Erros críticos
- Falhas de autenticação
- Problemas de performance
- Espaço em disco baixo

### 7.2 Métricas

- Taxa de erros
- Latência de requisições
- Uso de recursos
- Contagem de eventos
