# Regras para Verificar Versões de Dependências

## 1. Análise Inicial

- Verificar todas as dependências listadas no `requirements.txt`
- Identificar versões atuais e últimas versões disponíveis
- Documentar dependências críticas para o sistema

## 2. Verificação de Versões

- Usar `pip index versions [pacote]` para verificar versões disponíveis
- Verificar changelogs para mudanças significativas
- Identificar breaking changes entre versões

## 3. Testes de Compatibilidade

- Realizar testes de instalação com `--dry-run`
- Verificar conflitos entre dependências
- Testar em ambiente isolado antes de produção

## 4. Resolução de Conflitos

- Documentar conflitos encontrados
- Ajustar versões para resolver incompatibilidades
- Manter registro de decisões tomadas

## 5. Boas Práticas

- Sempre especificar versões exatas (exceto quando necessário range)
- Manter arquivo de requirements organizado por categorias
- Incluir comentários para decisões importantes

## 6. Processo de Atualização

- Criar branch específica para atualizações
- Testar mudanças em ambiente de desenvolvimento
- Documentar processo de rollback se necessário

## 7. Monitoramento de Segurança

- Usar `safety check` para verificar vulnerabilidades
- Manter registro de vulnerabilidades conhecidas
- Planejar atualizações de segurança

### Vulnerabilidades Conhecidas

1. gunicorn==21.2.0
   - CVE-2024-1135: Validação inadequada de headers Transfer-Encoding
   - Impacto: Possível HTTP Request Smuggling (HRS)
   - Observação: Mantida versão 21.2.0 por ser mais estável. Versão 22.0.0 também apresenta vulnerabilidades similares.
   - Mitigação: Usar em conjunto com proxy reverso que valida headers adequadamente

## 8. Ferramentas Úteis

- pip-tools para gerenciamento de dependências
- safety para verificação de segurança
- pip-audit para auditoria de dependências

## 9. Informações do Servidor de Produção

- Plataforma: Render
- SSH: ssh srv-ctmtqra3esus739sknb0@ssh.oregon.render.com
- Região: Oregon (US West)
- Tipo: Web Service

## 10. Troubleshooting via SSH

### Diagnóstico Inicial com ls -la

O comando `ls -la` é fundamental para o diagnóstico inicial no servidor por várias razões:

1. Estrutura do Projeto:

   - Revela a estrutura completa de diretórios
   - Mostra arquivos ocultos importantes (ex: .env, .gitignore)
   - Identifica permissões e propriedades dos arquivos

2. Verificação de Deployment:

   - Confirma se todos os arquivos foram deployados corretamente
   - Verifica datas de modificação dos arquivos
   - Identifica possíveis problemas de permissão

3. Localizando Arquivos Críticos:

   ```bash
   # Verificar diretório raiz
   ls -la /app/

   # Verificar diretório de logs
   ls -la /app/logs/

   # Verificar ambiente virtual
   ls -la /opt/venv/
   ```

4. Por que funciona melhor que outros comandos:
   - Não requer permissões especiais
   - Fornece visão completa do sistema de arquivos
   - Ajuda a identificar problemas de permissão ou arquivos faltantes

### minhas configs

Host render
HostName ssh.oregon.render.com
User srv-ctmtqra3esus739sknb0
IdentityFile ~/.ssh/id_ed25519
StrictHostKeyChecking no
UserKnownHostsFile /dev/null

### Comandos Úteis no Servidor

1. Logs e Monitoramento:

```bash
# Ver logs da aplicação
tail -f /var/log/app.log

# Monitorar uso de recursos
top
htop (se disponível)
```

2. Verificação de Dependências:

```bash
# Listar pacotes Python instalados
pip list

# Verificar versão específica
pip show [pacote]
```

3. Diagnóstico de Problemas:

```bash
# Verificar processos Python
ps aux | grep python

# Verificar portas em uso
netstat -tulpn

# Verificar status do serviço
systemctl status [nome-do-serviço]
```

4. Arquivos e Configurações:

```bash
# Verificar variáveis de ambiente
env | grep SUPABASE
env | grep HUGGINGFACE

# Verificar configurações
cat /etc/[nome-do-serviço]/config.yml
```

5. Testes Rápidos:

```bash
# Testar conexão com banco
python -c "from supabase import create_client; print('OK')"

# Verificar imports
python -c "import langchain; print(langchain.__version__)"
```

### Boas Práticas SSH

1. Segurança:

   - Nunca deixar sessão SSH aberta sem uso
   - Não modificar arquivos de configuração diretamente
   - Evitar alterações permanentes via SSH

2. Debugging:

   - Sempre fazer backup antes de alterações
   - Documentar comandos executados
   - Registrar resultados obtidos

3. Monitoramento:

   - Verificar logs antes e depois de mudanças
   - Monitorar uso de recursos durante testes
   - Documentar comportamentos anormais

4. Resolução de Problemas:
   - Começar com verificações básicas (logs, processos)
   - Escalar gradualmente a complexidade dos testes
   - Manter registro de todas as ações tomadas

## 11. Log Streaming no Render

### Configuração do Log Endpoint

Para configurar o streaming de logs no Render:

1. Log Endpoint:

   - Formato: `logs.papertrailapp.com:XXXXX`
   - Exemplo: `logs.papertrailapp.com:34302`
   - Substitua XXXXX pelo número da porta fornecido pelo seu provedor de logs

2. Provedores Suportados:

   - Papertrail
   - Datadog
   - LogDNA
   - Outros serviços compatíveis com syslog

3. Configuração:

   ```bash
   # Formato do endpoint
   [provedor].com:[porta]

   # Exemplo Papertrail
   logs.papertrailapp.com:34302

   # Exemplo LogDNA
   syslog-a.logdna.com:6514
   ```

4. Token (Opcional):

   - Alguns provedores requerem token de autenticação
   - Consulte a documentação específica do provedor
   - Mantenha o token seguro e nunca o compartilhe

5. Boas Práticas:
   - Configure filtros apropriados no provedor de logs
   - Defina retenção adequada dos logs
   - Monitore o uso de armazenamento de logs

## Serviço de Produção

### Serviço Único no Render

- Nome: coflow
- URL: api.coflow.com.br
- Tipo: Docker (Standard)
- Branch: main
- Região: Oregon
- Porta: 8000
- Health Check: /api/v1/health
- Repositório: diegofornalha/backend-rag-ia

**IMPORTANTE**: Este é o único serviço em produção até o momento. Não criar serviços adicionais sem autorização expressa.

### Configurações do Serviço

- Blueprint managed
- Internal Address: backend-rag-ia:8000
- Protocolo: HTTP
- Auto Deploy: Habilitado para branch main
