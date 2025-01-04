# Regras de SSH para Render

## 1. Configuração Inicial

### 1.1 Gerar Chave SSH

```bash
# Gerar nova chave ED25519 (recomendado)
ssh-keygen -t ed25519 -C "render-deploy"

# Adicionar ao agente SSH
ssh-add ~/.ssh/id_ed25519
```

### 1.2 Configuração do SSH Config

```bash
# ~/.ssh/config
Host render
    HostName ssh.oregon.render.com
    User srv-ctmtqra3esus739sknb0
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

## 2. Comandos SSH Úteis

### 2.1 Monitoramento

```bash
# Logs em tempo real
ssh render tail -f /var/log/render/*.log

# Status do serviço
ssh render systemctl status backend-rag-ia

# Logs do deploy
ssh render cat /etc/render/deploy.log
```

### 2.2 Recursos do Sistema

```bash
# Verificar recursos
ssh render top
ssh render free -h
ssh render df -h

# Verificar arquivos
ssh render ls -la /app/
ssh render ls -la /opt/venv/
```

## 3. Boas Práticas

### 3.1 Segurança

- Manter chaves SSH seguras e com permissões corretas
- Usar nomes descritivos para as chaves
- Revogar acesso de chaves não utilizadas
- Monitorar tentativas de acesso suspeitas

### 3.2 Manutenção

- Fazer backup das chaves SSH
- Rotacionar chaves periodicamente
- Manter registro de quais chaves estão em uso
- Documentar acessos e operações realizadas

### 3.3 Operações via SSH

- Preferir usar a interface web do Render para operações comuns
- Usar SSH apenas quando necessário para debugging ou operações específicas
- Documentar todas as alterações feitas via SSH
- Manter logs de comandos executados

## 4. Troubleshooting

### 4.1 Problemas Comuns

1. **Permission Denied**:

   - Verificar se a chave foi adicionada ao agente SSH
   - Confirmar se a chave foi registrada no Render
   - Verificar permissões do arquivo da chave

2. **Connection Refused**:

   - Verificar se o serviço está ativo
   - Confirmar configurações de firewall
   - Validar endereço do host

3. **Host Key Verification Failed**:
   - Limpar entrada antiga do known_hosts
   - Usar StrictHostKeyChecking=no no config

### 4.2 Verificações

```bash
# Testar conexão SSH
ssh -T render

# Verificar chaves carregadas
ssh-add -l

# Verificar permissões
ls -la ~/.ssh/
```

## 5. Integração com CI/CD

### 5.1 GitHub Actions

```yaml
- name: Configure SSH
  run: |
    mkdir -p ~/.ssh/
    echo "${{ secrets.RENDER_SSH_KEY }}" > ~/.ssh/id_ed25519
    chmod 600 ~/.ssh/id_ed25519
    ssh-keyscan ssh.render.com >> ~/.ssh/known_hosts
```

### 5.2 Variáveis Necessárias

- `RENDER_SSH_KEY`: Chave privada SSH (como secret)
- `RENDER_SERVICE_ID`: ID do serviço no Render
- `RENDER_API_KEY`: Chave API do Render (para operações via API)

## 6. Monitoramento e Logs

### 6.1 Logs do Sistema

```bash
# Logs do sistema
ssh render journalctl -u backend-rag-ia

# Logs do Docker
ssh render docker logs $(docker ps -q)

# Logs de autenticação
ssh render tail -f /var/log/auth.log
```

### 6.2 Métricas

```bash
# Uso de CPU
ssh render top -b -n 1

# Uso de memória
ssh render free -m

# Espaço em disco
ssh render df -h
```
