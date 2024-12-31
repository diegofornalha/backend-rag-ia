# Boas Práticas Docker

## 1. Imagem Base e Segurança

### 1.1 Escolha da Imagem Base

- Utilizar versões estáveis (ex: `python:3.11-slim`)
- Evitar versões alpha ou beta em produção
- Avaliar mudanças de versão com cautela

### 1.2 Segurança

- Utilizar Docker Scout para análise de vulnerabilidades
- Manter dependências atualizadas
- Evitar expor informações sensíveis em logs

## 2. Gerenciamento de Ambiente

### 2.1 Variáveis de Ambiente

- Usar `.env` para configurações locais
- Validar variáveis críticas (ex: SUPABASE_URL, SUPABASE_KEY)
- Implementar validações com Pydantic

### 2.2 Portas e Networking

- Verificar conflitos de porta antes da execução
- Liberar portas em uso quando necessário
- Documentar portas utilizadas

## 3. Workflow de Desenvolvimento

### 3.1 Comandos Úteis

```bash
# Parar containers usando uma porta específica
docker ps | grep <porta> | awk '{print $1}' | xargs -r docker stop

# Build e execução em um comando
docker build -t <tag> . && docker run -it -p <porta>:<porta> --env-file .env <tag>

# Comando completo para rodar o backend local
# 1. Para containers existentes
# 2. Reconstrói a imagem
# 3. Inicia o novo container
docker ps | grep 10000 | awk '{print $1}' | xargs -r docker stop && docker build -t backend:local . && docker run -it -p 10000:10000 --env-file .env backend:local
```

### 3.2 Automação

- Combinar comandos comuns em scripts
- Automatizar processos de build e teste
- Manter logs organizados

## 4. Troubleshooting

### 4.1 Logs e Debugging

- Monitorar logs do container
- Verificar variáveis de ambiente
- Validar configurações do Pydantic

### 4.2 Problemas Comuns

- Conflitos de porta
- Variáveis de ambiente faltantes
- Problemas de permissão
