# Regras do Docker

## PROIBIÇÕES ❌

1. **Criação de Arquivos**

   - ❌ NUNCA criar novos arquivos de regras sem verificar se já existem
   - ❌ NUNCA criar arquivos de regras fora da pasta `backend_rag_ia/regras_md`
   - ❌ NUNCA duplicar arquivos de regras em diferentes locais
   - ❌ NUNCA deixar arquivos soltos na raiz de `regras_md` - use sempre uma subpasta apropriada

2. **Gestão de Arquivos**

   - ❌ NUNCA sobrescrever arquivos existentes sem preservar o conteúdo anterior
   - ❌ NUNCA mover arquivos de regras para fora da estrutura definida
   - ❌ NUNCA renomear arquivos de regras sem atualizar todas as referências

3. **Organização**
   - ❌ NUNCA misturar regras de diferentes contextos na mesma pasta
   - ❌ NUNCA criar novas pastas sem seguir a estrutura existente
   - ❌ NUNCA ignorar a hierarquia de pastas estabelecida

## 1. Estrutura do Dockerfile

- O Dockerfile deve estar **APENAS** na raiz do projeto
- O requirements.txt deve estar **APENAS** na raiz do projeto
- Não criar Dockerfiles duplicados em subdiretórios
- O Render usa por padrão o Dockerfile e requirements.txt da raiz

## 2. Gestão de Variáveis de Ambiente

### Por que não usar .env diretamente no Dockerfile?

1. **Isolamento e Portabilidade**

   - O container Docker precisa ser autônomo e não depender de arquivos externos
   - Garante que o container funcionará em qualquer ambiente onde for executado
   - Evita problemas de "funciona na minha máquina"

2. **Segurança em Desenvolvimento**

   - Em desenvolvimento, usamos `.env` para manter as credenciais localmente
   - Em produção (ex: Render), as variáveis são configuradas no painel de controle
   - Dockerfiles específicos para testes não devem expor credenciais

3. **Problemas a Evitar**
   ```dockerfile
   # NÃO FAZER:
   COPY .env .  # Isso exporia credenciais
   ```
   - Evita exposição de credenciais no controle de versão
   - Previne conflitos entre ambientes
   - Facilita CI/CD

### Padrão Recomendado

```dockerfile
# Argumentos de build que podem ser sobrescritos
ARG SUPABASE_URL
ARG SUPABASE_KEY
ARG ENVIRONMENT=production

# Configura variáveis de ambiente
ENV SUPABASE_URL=${SUPABASE_URL} \
    SUPABASE_KEY=${SUPABASE_KEY} \
    ENVIRONMENT=${ENVIRONMENT} \
    PYTHONUNBUFFERED=1
```

### Formas de Uso

1. **Desenvolvimento (usando .env)**:

```bash
docker build -f Dockerfile \
  --build-arg SUPABASE_URL=$(grep SUPABASE_URL .env | cut -d '=' -f2) \
  --build-arg SUPABASE_KEY=$(grep SUPABASE_KEY .env | cut -d '=' -f2) \
  -t app-name .
```

2. **CI/CD (ex: Render)**:

```bash
docker build -f Dockerfile \
  --build-arg SUPABASE_URL=$SUPABASE_URL \
  --build-arg SUPABASE_KEY=$SUPABASE_KEY \
  --build-arg ENVIRONMENT=render \
  -t app-name .
```

3. **Runtime**:

```bash
docker run -e SUPABASE_URL=xxx -e SUPABASE_KEY=yyy app-name
```

## 3. Configurações Padrão

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

### Variáveis de Ambiente Básicas

```dockerfile
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
```

## 4. Boas Práticas

- Usar multi-stage build para otimização
- Manter apenas dependências necessárias
- Limpar cache e arquivos temporários
- Configurar healthcheck
- Usar imagens slim para reduzir tamanho
- Copiar apenas arquivos necessários

## 5. Segurança

- Não expor senhas ou chaves no Dockerfile
- Usar variáveis de ambiente para configurações sensíveis
- Manter permissões restritas nos diretórios
- Remover ferramentas de desenvolvimento no estágio final

## 6. Deploy no Render

- O Render detecta automaticamente o Dockerfile na raiz
- Não é necessário configurar comandos de build/start
- O Render usa as variáveis de ambiente configuradas na plataforma
- A porta padrão deve ser 10000 para compatibilidade

## 7. Quando Reconstruir a Imagem

1. Mudanças em Dependências:

   - Alterações no `requirements.txt`
   - Novas dependências do sistema
   - Atualizações de versões

2. Mudanças na Estrutura:

   - Renomeação de arquivos principais
   - Alterações no PYTHONPATH
   - Novos diretórios

3. Mudanças no Dockerfile:
   - Configurações do container
   - Comandos de build
   - Imagem base

### Comando para Reconstruir

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t fornalha/backend:latest . --push
```

### Verificação de Imagem

1. Verificar no Docker Hub: https://hub.docker.com/r/fornalha/backend
2. Confirmar tag `latest` atualizada
3. Verificar manifestos para ambas arquiteturas (amd64 e arm64)

## 8. Problemas Conhecidos e Otimizações de Cache

### 8.1 Problemas Conhecidos

1. **Dockerfile Vazio**

   - Sintoma: Erro "Dockerfile cannot be empty"
   - Causa: Problemas de codificação ou quebras de linha incorretas
   - Solução:
     - Verificar codificação do arquivo (deve ser UTF-8)
     - Remover caracteres especiais invisíveis
     - Usar LF ao invés de CRLF para quebras de linha

2. **Permissões de Push**
   - Sintoma: "denied: requested access to the resource is denied"
   - Causa: Falta de autenticação ou permissões no Docker Hub
   - Solução:
     - Executar `docker login` antes do push
     - Verificar existência do repositório
     - Confirmar permissões de acesso

### 8.2 Otimizações de Cache

1. **Ordenação de Camadas**

   ```dockerfile
   # ✅ CORRETO: Copiar requirements.txt primeiro
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Depois copiar o código fonte
   COPY . .
   ```

2. **Cache de Dependências**

   - Usar multi-stage builds para cachear dependências
   - Separar instalação de dependências do sistema e Python
   - Manter camadas mais estáveis no topo do Dockerfile

3. **Estratégias de Cache**

   ```dockerfile
   # Estágio de cache de dependências
   FROM python:3.11-slim as deps
   WORKDIR /deps
   COPY requirements.txt .
   RUN pip install --prefix=/install -r requirements.txt

   # Estágio de build
   FROM python:3.11-slim as builder
   COPY --from=deps /install /usr/local
   ```

4. **Pré-compilação**
   - Compilar pacotes Python em estágio separado
   - Usar `pip wheel` para criar wheels pré-compilados
   - Reutilizar wheels em builds subsequentes

### 8.3 Monitoramento de Cache

1. **Métricas de Build**

   - Tempo total de build
   - Hit rate do cache
   - Tamanho das camadas
   - Uso de recursos

2. **Comandos Úteis**

   ```bash
   # Verificar camadas e seu uso de cache
   docker history <image>

   # Limpar cache não utilizado
   docker builder prune

   # Inspecionar cache do buildx
   docker buildx du
   ```

3. **Boas Práticas**
   - Monitorar uso do cache regularmente
   - Limpar cache obsoleto periodicamente
   - Documentar padrões efetivos de cache
   - Manter registro de otimizações realizadas
