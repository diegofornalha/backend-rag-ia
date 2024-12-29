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

- Configurar notificações de status
- Monitorar logs através do dashboard
- Verificar métricas de performance
- Configurar alertas para falhas

## 5. Segurança

- Não commitar arquivos .env
- Usar variáveis de ambiente do Render
- Manter secrets seguros
- Seguir práticas de segurança do Docker
