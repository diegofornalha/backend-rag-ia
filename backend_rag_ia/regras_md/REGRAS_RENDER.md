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
- Testar conexão: `ssh srv-ctmtqra3esus739sknb0@ssh.oregon.render.com`

### 4.3 Configuração SSH Local

```bash
# Adicionar ao ~/.ssh/config
Host render
    HostName ssh.oregon.render.com
    User srv-ctmtqra3esus739sknb0
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
```

### 4.4 Comandos SSH Úteis

- Ver logs em tempo real: `ssh render tail -f /var/log/render/*.log`
- Status do serviço: `ssh render systemctl status backend-rag-ia`
- Verificar deploy: `ssh render cat /etc/render/deploy.log`
- Monitorar recursos: `ssh render top`
- Verificar arquivos: `ssh render ls -la /app/`
- Verificar ambiente virtual: `ssh render ls -la /opt/venv/`
- Verificar variáveis: `ssh render env | grep SUPABASE`

### 4.5 Boas Práticas SSH

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

# Regras Render

## Estrutura do Projeto para Render

### Organização dos Arquivos

1. **Módulo Principal** (`backend_rag_ia/`):

   - `app.py`: Aplicação FastAPI principal
   - `__init__.py`: Define o módulo e expõe a API pública
   - Demais arquivos da aplicação organizados em subpastas

2. **Raiz do Projeto**:
   - `main.py`: Ponto de entrada para o uvicorn
   - `render.yaml`: Configuração do Render
   - Arquivos de configuração

### Configuração do Render

1. **No `render.yaml`**:

   ```yaml
   services:
     - type: web
       name: backend-rag-ia
       env: docker
       region: oregon
       plan: starter
       healthCheckPath: /api/v1/health
       envVars:
         - key: PYTHONPATH
           value: /app
       dockerCommand: uvicorn main:app --host 0.0.0.0 --port 10000
   ```

2. **Variáveis de Ambiente**:
   - PYTHONPATH deve ser `/app`
   - Porta deve ser 10000
   - Demais variáveis configuradas no dashboard do Render

### Estrutura de Importações

1. **No `backend_rag_ia/__init__.py`**:

   ```python
   from .app import app
   __all__ = ['app']
   ```

2. **No `main.py` da raiz**:
   ```python
   from backend_rag_ia import app
   __all__ = ['app']
   ```

### Boas Práticas

1. **Isolamento**:

   - Manter aplicação isolada em seu próprio módulo
   - Usar `__init__.py` para definir API pública
   - Separar código da aplicação de configurações

2. **Organização**:

   - Manter raiz do projeto limpa
   - Usar estrutura modular
   - Seguir convenções Python (underscore vs hífen)

3. **Compatibilidade**:
   - Garantir que importações funcionem no ambiente Render
   - Manter PYTHONPATH consistente
   - Usar Docker para garantir ambiente consistente

### Verificação de Deploy

1. **Antes do Deploy**:

   - Confirmar que imagem Docker está atualizada
   - Verificar configurações no `render.yaml`
   - Testar localmente com mesma estrutura

2. **Durante Deploy**:

   - Monitorar logs do build
   - Verificar se importações estão corretas
   - Confirmar que variáveis de ambiente estão definidas

3. **Após Deploy**:
   - Testar endpoint de health check
   - Verificar logs da aplicação
   - Confirmar que estrutura de arquivos está correta

### Troubleshooting

1. **Erros Comuns**:

   - Problemas de importação: verificar PYTHONPATH e estrutura de arquivos
   - Falha no build: verificar Dockerfile e dependências
   - Erro de porta: confirmar que está usando porta 10000

2. **Soluções**:
   - Usar `__init__.py` para garantir que módulo é reconhecido
   - Manter estrutura consistente entre ambientes
   - Seguir convenções de nomeação Python
