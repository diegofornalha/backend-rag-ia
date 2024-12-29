# Regras do Docker

## 1. Estrutura do Dockerfile

- O Dockerfile deve estar **APENAS** na raiz do projeto
- O requirements.txt deve estar **APENAS** na raiz do projeto
- Não criar Dockerfiles duplicados em subdiretórios
- O Render usa por padrão o Dockerfile e requirements.txt da raiz

### 1.1 Organização de Arquivos Docker

- **Dockerfile** → Raiz do projeto (para deploy no Render)
- **requirements.txt** → Raiz do projeto (para deploy no Render)
- **docker-compose.yml** → Dentro da pasta específica do serviço (ex: `/monitoring`)
- **Arquivos de configuração** → Junto com o docker-compose.yml do serviço (ex: `loki-config.yaml`)

## 2. Configurações Padrão

### Multi-stage Build

```dockerfile
# Estágio de build
FROM python:3.11-slim as builder
# Estágio final
FROM python:3.11-slim
```

### Diretórios e Permissões

```dockerfile
RUN mkdir -p /app/logs /app/cache \
    && chmod -R 755 /app/logs /app/cache
```

### Variáveis de Ambiente

```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
```

## 3. Boas Práticas

- Usar multi-stage build para otimização
- Manter apenas dependências necessárias
- Limpar cache e arquivos temporários
- Configurar healthcheck
- Usar imagens slim para reduzir tamanho
- Copiar apenas arquivos necessários

## 4. Segurança

- Não expor senhas ou chaves no Dockerfile
- Usar variáveis de ambiente para configurações sensíveis
- Manter permissões restritas nos diretórios
- Remover ferramentas de desenvolvimento no estágio final

## 5. Deploy no Render

- O Render detecta automaticamente o Dockerfile na raiz
- Não é necessário configurar comandos de build/start
- O Render usa as variáveis de ambiente configuradas na plataforma
- A porta padrão deve ser 10000 para compatibilidade
