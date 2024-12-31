# Regras Docker

> ⚠️ Este documento contém as regras para build, verificação e deploy de imagens Docker.

## 1. Build

### Checklist Pré-Build

✅ **Verificar**:

- Dockerfile na raiz
- requirements.txt atualizado
- Variáveis de ambiente configuradas

### Comando de Build

```bash
# Build multi-plataforma
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t fornalha/backend:latest \
  . --push
```

## 2. Verificação de Imagens

### Após Build

1. **Verificar Build**:

   ```bash
   # Verificar arquiteturas
   docker manifest inspect fornalha/backend:latest | grep -A 3 "platform"
   ```

2. **Verificar Layers**:
   ```bash
   # Histórico de camadas
   docker history fornalha/backend:latest
   ```

### Checklist de Produção

✅ **Requisitos**:

- Pull bem sucedido
- Manifesto multi-plataforma
- Tamanho otimizado
- Cache configurado
- Sem vulnerabilidades
- Portas corretas

## 3. Ambientes

### Compatibilidade

1. **Local (Mac/ARM)**:

   ```bash
   docker run --rm fornalha/backend:latest python -c "print('OK')"
   ```

2. **CI (Linux/AMD64)**:

   - GitHub Actions
   - Testes automatizados

3. **Produção (Render)**:
   - Linux/AMD64
   - Configurações específicas

## 4. Manutenção

### Quando Reconstruir

1. **Dependências**:

   - Novos pacotes
   - Atualizações
   - Sistema base

2. **Projeto**:

   - Estrutura alterada
   - Novos diretórios
   - Configurações

3. **Dockerfile**:
   - Nova imagem base
   - Novos comandos
   - Otimizações

### Comandos Úteis

```bash
# Verificar status
docker inspect fornalha/backend:latest

# Verificar tags
docker image ls fornalha/backend

# Testar execução
docker run --rm fornalha/backend:latest python -c "print('OK')"
```

## 5. Critérios de Validação

✅ **Sucesso**:

- Imagem publicada
- Multi-plataforma OK
- Tags atualizadas
- Tamanho otimizado
- Metadata completo

❌ **Falha se**:

- Build falhou
- Testes falhando
- Vulnerabilidades
- Tamanho excessivo
