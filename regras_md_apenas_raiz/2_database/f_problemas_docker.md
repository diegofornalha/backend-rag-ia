# Problemas Conhecidos do Docker

## 1. Problemas de Build

### 1.1 Dockerfile Vazio

**Problema**: Build falha com erro "Dockerfile cannot be empty"

**Sintomas**:

- Erro ao tentar fazer build da imagem
- Mensagem indicando que o Dockerfile está vazio mesmo quando tem conteúdo
- Falha ao detectar instruções do Dockerfile

**Causas**:

1. Problemas de codificação do arquivo
2. Quebras de linha incorretas (CRLF vs LF)
3. Caracteres especiais invisíveis
4. Problemas de permissão de leitura

**Soluções**:

1. Verificar e corrigir codificação:

   ```bash
   # Verificar codificação
   file -i Dockerfile

   # Converter para UTF-8 se necessário
   iconv -f ISO-8859-1 -t UTF-8 Dockerfile > Dockerfile.new
   mv Dockerfile.new Dockerfile
   ```

2. Corrigir quebras de linha:

   ```bash
   # Converter CRLF para LF
   dos2unix Dockerfile

   # Ou usando sed
   sed -i 's/\r$//' Dockerfile
   ```

3. Remover caracteres especiais:
   ```bash
   # Remover caracteres invisíveis
   tr -cd '[:print:]\n' < Dockerfile > Dockerfile.new
   mv Dockerfile.new Dockerfile
   ```

### 1.2 Problemas de Push

**Problema**: Push falha com erro de acesso negado

**Sintomas**:

- Erro "denied: requested access to the resource is denied"
- Falha ao tentar fazer push da imagem
- Problemas de autenticação

**Causas**:

1. Falta de login no Docker Hub
2. Repositório inexistente
3. Permissões insuficientes
4. Token expirado

**Soluções**:

1. Autenticação:

   ```bash
   # Login no Docker Hub
   docker login

   # Verificar status do login
   docker info
   ```

2. Verificar repositório:

   ```bash
   # Listar repositórios
   curl -s -H "Authorization: Bearer $TOKEN" https://hub.docker.com/v2/repositories/$USERNAME/

   # Criar repositório se necessário
   curl -s -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"namespace":"'$USERNAME'","name":"'$REPO'"}' \
        https://hub.docker.com/v2/repositories/
   ```

## 2. Problemas de Cache

### 2.1 Cache Ineficiente

**Problema**: Builds demorados por cache não otimizado

**Sintomas**:

- Builds sempre recompilam todas as camadas
- Cache não é reutilizado entre builds
- Alto consumo de recursos e tempo

**Causas**:

1. Ordem incorreta das camadas
2. Invalidação desnecessária do cache
3. Falta de estratégia de cache

**Soluções**:

1. Otimizar ordem das camadas:

   ```dockerfile
   # ✅ CORRETO: Dependências primeiro
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Código fonte depois
   COPY . .
   ```

2. Implementar multi-stage build:

   ```dockerfile
   # Estágio de dependências
   FROM python:3.11-slim as deps
   WORKDIR /deps
   COPY requirements.txt .
   RUN pip install --prefix=/install -r requirements.txt

   # Estágio de build
   FROM python:3.11-slim as builder
   COPY --from=deps /install /usr/local
   ```

3. Usar buildx com cache:
   ```bash
   # Build com cache local
   docker buildx build --cache-from type=local,src=/path/to/cache \
                      --cache-to type=local,dest=/path/to/cache \
                      -t myimage .
   ```

### 2.2 Monitoramento e Manutenção

**Ferramentas Úteis**:

```bash
# Análise de camadas
docker history <image>

# Limpeza de cache
docker builder prune

# Inspeção de cache
docker buildx du
```

**Boas Práticas**:

1. Monitorar métricas de build:

   - Tempo total
   - Hit rate do cache
   - Tamanho das camadas
   - Uso de recursos

2. Manutenção regular:
   - Limpar cache obsoleto
   - Otimizar Dockerfile
   - Documentar melhorias
   - Manter registro de problemas

## 3. Registro de Melhorias

### 3.1 Melhorias Implementadas

| Data       | Problema          | Solução                 | Impacto             |
| ---------- | ----------------- | ----------------------- | ------------------- |
| 2024-01-20 | Build vazio       | Correção de codificação | Build funcionando   |
| 2024-01-21 | Cache ineficiente | Multi-stage build       | -50% tempo de build |

### 3.2 Melhorias Pendentes

1. **Alta Prioridade**:

   - Implementar cache distribuído
   - Otimizar tamanho da imagem base
   - Melhorar estratégia de layers

2. **Média Prioridade**:

   - Automatizar limpeza de cache
   - Implementar métricas de build
   - Melhorar documentação

### Comandos de Build por Ambiente

1. **Desenvolvimento Local (Mac para Docker Hub)**:

   ```bash
   # Necessário --platform para compatibilidade Mac/Linux
   docker buildx build --platform linux/amd64,linux/arm64 -t fornalha/backend:latest . --push
   ```

2. **Render (Build Automático)**:
   ```bash
   # O Render usa este comando internamente
   docker build -t registry.render.com/backend-rag-ia:latest .
   ```

**Por que a diferença?**

- Mac usa arquitetura ARM (M1/M2), Render usa Linux/amd64
- `--platform` é necessário apenas quando buildando do Mac para Linux
- Render já configura automaticamente o registro e a tag correta
- Não é necessário fazer push manual para o Render, ele puxa direto do GitHub

**Dicas**

- Para desenvolvimento local: use `--platform` para garantir compatibilidade
- Para Render: deixe o build automático fazer seu trabalho
- Mantenha o Dockerfile compatível com ambas plataformas
