# SSH no Render: Guia Completo

## Índice

1. [Contexto](#1-contexto)
2. [Configuração de Acesso](#2-configuração-de-acesso)
3. [Limitações](#3-limitações)
4. [Casos de Uso](#4-casos-de-uso)
5. [Boas Práticas](#5-boas-práticas)
6. [Alternativas](#6-alternativas)
7. [Comandos Úteis](#7-comandos-úteis)
8. [Troubleshooting Comum](#8-troubleshooting-comum)
9. [Recursos Adicionais](#9-recursos-adicionais)
10. [Configurações SSH](#configurações-ssh-no-render)
11. [Ambiente Python](#ambiente-python)
12. [Sistema de Arquivos](#sistema-de-arquivos)
13. [Limitações de Acesso](#limitações-de-acesso)
14. [Ambiente de Rede](#ambiente-de-rede)
15. [Variáveis de Ambiente](#variáveis-de-ambiente)

## 1. Contexto

O SSH (Secure Shell) no Render é uma ferramenta de diagnóstico que oferece acesso limitado ao ambiente do serviço. É importante entender que este não é o ambiente de produção real, mas sim um ambiente isolado para troubleshooting básico.

## 2. Configuração de Acesso

### Credenciais

- **Host:** `ssh.oregon.render.com`
- **Usuário:** `srv-ctmtqra3esus739sknb0`
- **Formato do Comando:**
  ```bash
  ssh srv-ctmtqra3esus739sknb0@ssh.oregon.render.com
  ```

### Estrutura de Diretórios

1. Diretório Home (`/root`):

   ```
   ├── .bashrc
   ├── .profile
   ├── .ssh/
   └── .cache/
   ```

2. Ambiente Python (`/opt/venv`):
   ```
   ├── bin/
   ├── include/
   ├── lib/
   ├── lib64 -> lib
   ├── pyvenv.cfg
   └── share/
   ```

## 3. Limitações

### Comandos Indisponíveis

- `ps` (processos)
- `journalctl` (logs do sistema)
- `git` (controle de versão)
- Outros utilitários comuns de sistema

### Diretórios Restritos

- `/opt/render` (não acessível)
- `/var/log` (logs limitados)
- Diretório da aplicação (não acessível diretamente)

### Restrições de Ambiente

- Sem acesso ao ambiente de produção real
- Limitações de memória e CPU
- Sem persistência entre sessões
- Comandos de sistema limitados

## 4. Casos de Uso

### Recomendado Para

1. Diagnósticos Básicos:

   - Verificar estrutura de diretórios
   - Testar conectividade
   - Validar configurações

2. Verificações de Ambiente:
   - Versão do Python
   - Pacotes instalados
   - Variáveis de ambiente básicas

### Não Recomendado Para

1. Operações Críticas:

   - Deploy de aplicações
   - Modificações no sistema
   - Debugging complexo

2. Monitoramento:
   - Logs em tempo real
   - Métricas de performance
   - Estado da aplicação

## 5. Boas Práticas

### Segurança

- Não armazenar dados sensíveis
- Limitar tempo de sessão
- Usar apenas para diagnóstico
- Não compartilhar credenciais

### Eficiência

- Preparar comandos antes de conectar
- Manter scripts de diagnóstico prontos
- Documentar descobertas importantes
- Usar em conjunto com dashboard

## 6. Alternativas

### Para Logs

- Dashboard do Render
- API do Render
- Serviços de log externos

### Para Monitoramento

- Métricas do Render
- Healthchecks
- Serviços de monitoramento externos

## 7. Comandos Úteis

```bash
# Verificar versão do Python
python3 -V

# Listar pacotes instalados
pip list

# Verificar variáveis de ambiente
env | grep RENDER_

# Buscar arquivos
find / -type f -name "*.py" 2>/dev/null

# Testar conectividade
curl -v https://api.render.com
```

## 8. Troubleshooting Comum

### Problema de Conexão

```bash
# Erro: Connection refused
# Solução: Verificar status do serviço no dashboard
```

### Acesso Negado

```bash
# Erro: Permission denied
# Solução: Verificar credenciais SSH
```

## 9. Recursos Adicionais

- [Documentação Oficial do Render](https://render.com/docs)
- [Guia de Troubleshooting](https://render.com/docs/troubleshooting-deploys)
- [FAQ do SSH](https://render.com/docs/ssh)

# Configurações SSH no Render

## Estrutura de Diretórios

O Render utiliza uma estrutura personalizada para as configurações SSH:

```
/opt/render-ssh/
├── sshd_config.d/
│   ├── docker-nonroot
│   ├── docker-root
│   ├── native-envs
│   └── partials/
│       ├── base
│       ├── docker
│       └── root
├── var/
│   ├── run/
│   │   └── sshd.pid
│   └── ssh/
│       └── ssh_host_ed25519_key
└── etc/
    └── ssh/
        ├── user_ca_keys
        └── ssh_host_ed25519_key-cert.pub
```

## Configurações de Segurança

### Autenticação

- Apenas autenticação por chave pública é permitida
- Autenticação por senha está desabilitada
- Autenticação baseada em host está desabilitada
- Autenticação interativa por teclado está desabilitada

### Algoritmos e Criptografia

- **KexAlgorithms**:

  - curve25519-sha256@libssh.org
  - ecdh-sha2-nistp521
  - ecdh-sha2-nistp384
  - ecdh-sha2-nistp256
  - diffie-hellman-group-exchange-sha256

- **Ciphers**:
  - chacha20-poly1305@openssh.com
  - aes256-gcm@openssh.com
  - aes128-gcm@openssh.com
  - aes256-ctr
  - aes192-ctr
  - aes128-ctr

### Limitações e Restrições

- Todos os comandos são forçados através de `/opt/render-ssh/bin/setup-env-run-cmd.sh`
- Penalidades por fonte (PerSourcePenalties) estão desativadas devido ao proxy
- O servidor SFTP está configurado em `/opt/render-ssh/bin/sftp-server`

## Observações Importantes

1. O ambiente SSH é isolado e tem acesso restrito a certas funcionalidades
2. Logs detalhados são mantidos (LogLevel VERBOSE)
3. O sistema usa certificados ED25519 para autenticação do host
4. Conexões são feitas através de um proxy, o que afeta algumas funcionalidades de segurança

## Boas Práticas

1. Sempre use chaves SSH para autenticação
2. Mantenha suas chaves privadas seguras
3. Esteja ciente das limitações do ambiente isolado
4. Use o SFTP quando necessário para transferência de arquivos

## Troubleshooting

1. Se encontrar o erro "server gave bad signature for ED25519 key", isso é esperado e não afeta a funcionalidade
2. Problemas de acesso podem estar relacionados às restrições do ambiente isolado
3. Verifique os logs em caso de problemas de conexão

## Ambiente Python

### Versão e Localização

- Python versão: 3.12.8
- Ambiente virtual: `/opt/venv/`
- Python executável: `/usr/local/bin/python` (symlink)

### Ferramentas Disponíveis

- **Web Servers**:
  - gunicorn
  - uvicorn
- **Machine Learning**:
  - huggingface-cli
  - transformers-cli
  - torch
  - langchain-server
  - langsmith
- **Utilitários**:
  - pip (24.3.1)
  - dotenv
  - httpx
  - tqdm
  - nltk
- **Ferramentas JSON**:
  - jsondiff
  - jsonpatch
  - jsonpointer
- **Criptografia**:
  - pyrsa-decrypt
  - pyrsa-encrypt
  - pyrsa-keygen
  - pyrsa-sign
  - pyrsa-verify

### Observações do Ambiente

1. O ambiente virtual é gerenciado pelo root
2. Todas as ferramentas estão instaladas no diretório `/opt/venv/bin/`
3. Python é instalado globalmente em `/usr/local/bin/`
4. Symlinks são usados para versões específicas do Python

### Boas Práticas

1. Use o ambiente virtual para todas as operações Python
2. Mantenha as dependências atualizadas via requirements.txt
3. Verifique compatibilidade com Python 3.12.8
4. Use as ferramentas fornecidas ao invés de instalar duplicatas

## Sistema de Arquivos

### Estrutura de Montagem

- **Sistema Principal**:
  - Tipo: overlay
  - Tamanho: 291G
  - Usado: 236G (81%)
  - Disponível: 56G
- **Diretórios Temporários**:
  - `/dev`: 64M (tmpfs)
  - `/dev/shm`: 64M (shm)
  - `/tmp`: montado em /dev/root
- **Diretórios Especiais**:
  - `/etc/secrets`: 56G (tmpfs)
  - `/opt/render-ssh/etc/ssh`: 56G (tmpfs)
- **Diretórios do Sistema**:
  - `/proc/acpi`: 31G (tmpfs)
  - `/proc/scsi`: 31G (tmpfs)
  - `/sys/firmware`: 31G (tmpfs)

### Diretório /opt

- `render-ssh/`: Configurações e binários SSH (permissões: drwxrwxrwx)
- `venv/`: Ambiente virtual Python (permissões: drwxr-xr-x)

### Observações Importantes

1. O sistema usa overlay filesystem para otimização
2. Diretórios sensíveis são montados em tmpfs para segurança
3. Espaço em disco é compartilhado entre todos os serviços
4. Alguns diretórios têm permissões especiais para o sistema Render

### Boas Práticas

1. Monitore o uso do disco (81% usado)
2. Use diretórios temporários para arquivos transitórios
3. Respeite as permissões dos diretórios
4. Mantenha os logs rotacionados para economizar espaço

## Limitações de Acesso

### Comandos Restritos

1. **Gerenciamento de Processos**:
   - `ps`: Não disponível
   - `top`: Não disponível
   - `htop`: Não disponível
2. **Gerenciamento de Serviços**:
   - `systemctl`: Não disponível
   - `service`: Não disponível
   - `init.d`: Não disponível
3. **Monitoramento de Sistema**:
   - `netstat`: Não disponível
   - `lsof`: Não disponível
   - `strace`: Não disponível

### Razões para Restrições

1. Segurança do ambiente isolado
2. Prevenção de interferência entre serviços
3. Isolamento de recursos
4. Proteção da infraestrutura Render

### Alternativas Recomendadas

1. Use o dashboard Render para monitoramento
2. Configure logs adequados na aplicação
3. Utilize métricas de aplicação
4. Implemente health checks

### Boas Práticas

1. Planeje o monitoramento via API Render
2. Implemente logs detalhados na aplicação
3. Use ferramentas de APM compatíveis
4. Mantenha documentação de troubleshooting

## Ambiente de Rede

### Configuração DNS

- **Domínios de Busca**:
  - `own-ctm6tfdumphs73ddibh0.svc.cluster.local`
  - `svc.cluster.local`
  - `cluster.local`
  - `us-west-2.compute.internal`
- **Servidores DNS**:
  - `169.254.20.10`
  - `10.221.0.10`
- **Opções**:
  - `ndots:5`

### Conectividade Externa

- **API Render**:
  - Acessível via HTTPS
  - Proteção Cloudflare ativa
  - Headers de segurança implementados:
    - `Strict-Transport-Security`
    - `X-Frame-Options: DENY`
    - `X-XSS-Protection: 1`
    - `Referrer-Policy: same-origin`

### Observações de Rede

1. Ambiente roda em cluster Kubernetes
2. Localizado na região us-west-2 (Oregon)
3. Usa rede interna do cluster
4. Proteção Cloudflare na camada de API

### Boas Práticas

1. Use HTTPS para todas as conexões
2. Respeite os headers de segurança
3. Configure timeouts adequados
4. Implemente retry logic para resiliência

### Limitações

1. Acesso direto a portas restritas
2. Comandos de rede limitados
3. Conexões apenas via proxy Render
4. Sem acesso direto ao Kubernetes

## Variáveis de Ambiente

### Informações do Serviço

- **Identificação**:

  - `RENDER_SERVICE_ID=srv-ctmtqra3esus739sknb0`
  - `RENDER_SERVICE_NAME=backend-rag-ia`
  - `RENDER_SERVICE_TYPE=web`
  - `RENDER_INSTANCE_ID=srv-ctmtqra3esus739sknb0-788df49d7d-9764s`

- **URLs e Endpoints**:
  - `RENDER_EXTERNAL_URL=https://backend-rag-ia.onrender.com`
  - `RENDER_EXTERNAL_HOSTNAME=backend-rag-ia.onrender.com`
  - `RENDER_INTERNAL_HOSTNAME=srv-ctmtqra3esus739sknb0.own-ctm6tfdumphs73ddibh0.svc.cluster.local`
  - `RENDER_DEPLOY_HOOK=https://api.render.com/deploy/srv-ctmtqra3esus739sknb0?key=Wi7d95yz5_s`

### Configurações de Ambiente

- **Runtime**:

  - `PYTHON_VERSION=3.12.0`
  - `PYTHONUNBUFFERED=1`
  - `PYTHONDONTWRITEBYTECODE=1`
  - `PORT=8000`
  - `HOST=0.0.0.0`
  - `DEBUG=false`
  - `ENVIRONMENT=production`

- **Integrações**:
  - `LANGCHAIN_API_KEY=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`
  - `LANGCHAIN_PROJECT=keepai`
  - `LANGCHAIN_TRACING_V2=true`
  - `LANGCHAIN_ENDPOINT=https://api.smith.langchain.com`
  - `LANGCHAIN_CACHE_DIR=/app/cache/langchain`
  - `GEMINI_API_KEY=[REDACTED]`
  - `GITHUB_TOKEN=[REDACTED]`
  - `SUPABASE_URL=https://uaxnbpzamzxradpmccse.supabase.co`
  - `SUPABASE_KEY=[REDACTED]`

### Configurações Git

- `RENDER_GIT_REPO_SLUG=diegofornalha/backend-rag-ia`
- `RENDER_GIT_BRANCH=main`
- `RENDER_GIT_COMMIT=d530a501e78458e558e19e947983ee9903af0885`
- `IS_PULL_REQUEST=false`

### Observações Importantes

1. Chaves sensíveis são armazenadas como variáveis de ambiente
2. Configurações específicas do Render são prefixadas com `RENDER_`
3. Ambiente é configurado para produção
4. Integrações com serviços externos são gerenciadas via variáveis

### Boas Práticas

1. Nunca exponha chaves sensíveis
2. Use variáveis de ambiente para configuração
3. Mantenha documentação atualizada
4. Faça rotação periódica das chaves

### Segurança

1. Chaves de API devem ser rotacionadas regularmente
2. Tokens devem ter o mínimo de permissões necessárias
3. Monitore o uso das chaves de API
4. Implemente logs de auditoria
