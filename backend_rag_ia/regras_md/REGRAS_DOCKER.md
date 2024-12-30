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

## Estrutura do Projeto para Docker

### Organização dos Arquivos

1. **Módulo Principal** (`backend_rag_ia/`):

   - `app.py`: Aplicação FastAPI principal
   - `__init__.py`: Define o módulo e expõe a API pública
   - Demais arquivos da aplicação organizados em subpastas

2. **Raiz do Projeto**:
   - `main.py`: Ponto de entrada para o uvicorn
   - `Dockerfile`: Configuração do container
   - `requirements.txt`: Dependências
   - Arquivos de configuração

### Importações e PYTHONPATH

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

3. **No Dockerfile**:
   ```dockerfile
   ENV PYTHONPATH=/app
   ```

### Quando Reconstruir a Imagem

1. Mudanças em Dependências:

   - Alterações no `requirements.txt`
   - Novas dependências do sistema
   - Atualizações de versões

2. Mudanças na Estrutura:

   - Renomeação de arquivos principais (ex: main.py → app.py)
   - Alterações no PYTHONPATH
   - Novos diretórios que precisam ser copiados

3. Mudanças no Dockerfile:

   - Configurações do container
   - Comandos de build
   - Imagem base

4. Mudanças em Arquivos:

   - Novos assets
   - Arquivos de configuração
   - Arquivos copiados para o container

5. Mudanças de Ambiente:
   - Variáveis de ambiente
   - Configurações de runtime

### Comando para Reconstruir

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t fornalha/backend:latest . --push
```

### Verificação de Imagem

Para verificar se a imagem foi publicada e atualizada:

1. Verificar no Docker Hub: https://hub.docker.com/r/fornalha/backend
2. Confirmar tag `latest` atualizada
3. Verificar manifestos para ambas arquiteturas (amd64 e arm64)

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
   - Garantir que importações funcionem em todos ambientes
   - Manter PYTHONPATH consistente
   - Testar em diferentes plataformas
