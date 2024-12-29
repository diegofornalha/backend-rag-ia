# Regras do Ambiente Render

## Ambiente SSH do Render

### Acesso

- Host: `ssh.oregon.render.com`
- Usuário: `srv-ctmtqra3esus739sknb0`
- Formato: `ssh srv-ctmtqra3esus739sknb0@ssh.oregon.render.com`

### Estrutura do Ambiente

1. Diretório Home (`/root`):

   - `.bashrc`
   - `.profile`
   - `.ssh/`
   - `.cache/`

2. Ambiente Python (`/opt/venv`):
   - `bin/`
   - `include/`
   - `lib/`
   - `lib64 -> lib`
   - `pyvenv.cfg`
   - `share/`

### Limitações

1. Comandos Indisponíveis:

   - `ps`
   - `journalctl`
   - Outros utilitários de sistema

2. Diretórios Restritos:
   - Sem acesso ao `/opt/render`
   - Logs limitados em `/var/log`

### Boas Práticas

1. Usar para Diagnóstico Básico:

   - Verificar estrutura de diretórios
   - Confirmar instalação de pacotes
   - Testar configurações básicas

2. Para Logs Completos:
   - Usar Dashboard do Render
   - Usar API do Render
   - Configurar logs externos

### Notas Importantes

- Este é um ambiente isolado de diagnóstico
- Não é o mesmo ambiente onde a aplicação roda
- Acesso limitado por razões de segurança
- Útil para verificações básicas de configuração

## Comandos Úteis para Monitoramento

```bash
# Verificar estrutura do venv
cd /opt/venv && ls -la

# Verificar pacotes instalados
cat /var/log/apt/history.log

# Buscar arquivos específicos
find / -type f -name "app.py" 2>/dev/null
```

## Problemas Comuns e Soluções

### 1. Erros de Instalação de Dependências

- Sempre use aspas em versões com operadores: `"httpx>=0.24.0,<0.26.0"`
- Ative o ambiente virtual antes do pip install: `. /opt/venv/bin/activate`
- Mantenha dependências em camadas no Dockerfile para melhor cache
- Verifique compatibilidade entre versões no PyPI

### 2. Problemas de Build

- Monitore builds via API do Render:
  ```bash
  curl -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/$SERVICE_ID/deploys"
  ```
- Use multi-stage builds no Dockerfile
- Limpe caches e arquivos temporários
- Mantenha logs organizados por seção

### 3. Ambiente e Configuração

- Configure todas as variáveis de ambiente no dashboard
- Use .env apenas para desenvolvimento local
- Mantenha versões de Python compatíveis
- Configure PYTHONUNBUFFERED=1 para logs adequados

### 4. Monitoramento e Logs

1. Via Dashboard:

   - Logs completos de build e runtime
   - Histórico de deploys
   - Métricas de performance

2. Via API:

   - Status de deploys em tempo real
   - Logs de build
   - Eventos do serviço

3. Via SSH (Limitado):
   - Verificações básicas
   - Testes de conectividade
   - Diagnósticos simples

### 5. Boas Práticas

1. Build:

   - Use multi-stage builds
   - Minimize camadas do Docker
   - Mantenha dependências atualizadas
   - Documente mudanças importantes

2. Deploy:

   - Configure healthchecks
   - Use zero-downtime deploys
   - Monitore logs constantemente
   - Mantenha backups de configurações

3. Manutenção:
   - Atualize dependências regularmente
   - Monitore uso de recursos
   - Mantenha documentação atualizada
   - Faça rollbacks quando necessário

### 6. Healthchecks

1. Configuração:

   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
       CMD curl -f http://localhost:8000/api/v1/health || exit 1
   ```

2. Endpoint:
   ```python
   @app.get("/api/v1/health")
   def health_check():
       return {"status": "healthy"}
   ```

### 7. Comandos Úteis para Troubleshooting

```bash
# Verificar status do deploy
curl -H "Authorization: Bearer $RENDER_API_KEY" \
    "https://api.render.com/v1/services/$SERVICE_ID/deploys?limit=1"

# Disparar novo deploy
curl -X POST "https://api.render.com/deploy/$SERVICE_ID?key=$DEPLOY_KEY"

# Verificar logs (via SSH)
cd /var/log && cat *.log

# Verificar ambiente Python
python3 -V && pip list
```

## Meta-Regras de Documentação

### 1. Atualizações Automáticas

- Toda nova solução deve ser documentada imediatamente
- Ao resolver um problema, adicionar à seção apropriada
- Incluir exemplos práticos sempre que possível
- Manter padrão de formatação markdown

### 2. Organização do Conhecimento

1. Identificação:

   - Observar padrões de problemas
   - Identificar soluções reutilizáveis
   - Capturar comandos úteis

2. Documentação:

   - Adicionar à seção apropriada
   - Incluir contexto do problema
   - Documentar passos da solução
   - Adicionar exemplos de código

3. Manutenção:
   - Revisar periodicamente
   - Atualizar soluções obsoletas
   - Remover informações duplicadas
   - Manter exemplos atualizados

### 3. Formato de Documentação

````markdown
### Nome do Problema

1. Contexto:

   - Descrição do problema
   - Sintomas comuns
   - Impacto no sistema

2. Solução:

   - Passos para resolver
   - Comandos necessários
   - Configurações importantes

3. Exemplo:
   ```bash
   # Comando exemplo
   comando --flag valor
   ```
````

4. Notas:
   - Observações importantes
   - Casos especiais
   - Limitações conhecidas

```

```
