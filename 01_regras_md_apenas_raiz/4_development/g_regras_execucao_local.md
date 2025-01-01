# Regras de Execução Local do Backend

> ⚠️ Este documento define as regras e métodos para executar o backend em ambiente local.
> Inclui diferentes abordagens de execução e troubleshooting.

## 1. Métodos de Execução

### 1.1 Python Direto

```bash
# Método 1 - Usando o arquivo main.py na raiz
python main.py

# Método 2 - Usando uvicorn diretamente (recomendado para desenvolvimento)
uvicorn backend_rag_ia.api.main:app --reload --port 10000
```

### 1.2 Docker

```bash
# Comando completo para rodar com Docker
docker ps | grep 10000 | awk '{print $1}' | xargs -r docker stop && \
docker build -t backend:local . && \
docker run -it -p 10000:10000 --env-file .env backend:local
```

## 2. Configuração do Ambiente

### 2.1 Pré-requisitos

1. **Python**:

   - Versão 3.11 ou superior
   - Ambiente virtual ativado
   - Dependências instaladas via `requirements.txt`

2. **Docker** (opcional):

   - Docker Desktop instalado e rodando
   - Permissões adequadas configuradas

3. **Variáveis de Ambiente**:
   - Arquivo `.env` configurado
   - Todas as variáveis necessárias definidas
   - Credenciais e chaves de API configuradas

### 2.2 Portas e Endpoints

1. **Porta Padrão**: 10000
2. **URLs Importantes**:
   - API: http://localhost:10000
   - Swagger: http://localhost:10000/docs
   - ReDoc: http://localhost:10000/redoc

## 3. Desenvolvimento Local

### 3.1 Hot Reload

- Disponível usando uvicorn com flag `--reload`
- Atualiza automaticamente ao modificar arquivos
- Ideal para desenvolvimento ativo
- Não recomendado para produção

### 3.2 Logs e Debugging

1. **Logs**:

   - Nível de log configurável via variável de ambiente
   - Logs detalhados no terminal
   - Erros e stacktraces visíveis

2. **Debugging**:
   - Possível anexar debugger
   - Breakpoints funcionam normalmente
   - Suporte a ferramentas como VS Code Debug

## 4. Troubleshooting

### 4.1 Problemas Comuns

1. **Porta em Uso**:

   ```bash
   # Verificar processo usando a porta
   lsof -i :10000

   # Matar processo se necessário
   kill -9 $(lsof -t -i:10000)
   ```

2. **Dependências**:

   ```bash
   # Reinstalar dependências
   pip install -r requirements.txt

   # Verificar ambiente virtual
   which python
   ```

3. **Docker**:

   ```bash
   # Limpar containers antigos
   docker system prune

   # Reconstruir imagem do zero
   docker build --no-cache -t backend:local .
   ```

### 4.2 Checklist de Verificação

1. **Ambiente**:

   - [ ] Diretório correto
   - [ ] Ambiente virtual ativado
   - [ ] Dependências instaladas
   - [ ] .env configurado

2. **Execução**:

   - [ ] Porta 10000 livre
   - [ ] Permissões adequadas
   - [ ] Logs sem erros
   - [ ] API respondendo

3. **Docker**:
   - [ ] Docker rodando
   - [ ] Imagem construída
   - [ ] Portas mapeadas
   - [ ] Variáveis de ambiente passadas

## 5. Boas Práticas

1. **Desenvolvimento**:

   - Usar hot reload para agilidade
   - Manter logs em nível adequado
   - Testar endpoints após mudanças
   - Verificar documentação Swagger

2. **Docker**:

   - Manter imagem atualizada
   - Limpar containers antigos
   - Usar volumes quando necessário
   - Otimizar Dockerfile

3. **Segurança**:
   - Não expor .env
   - Usar HTTPS em produção
   - Proteger endpoints sensíveis
   - Validar inputs
