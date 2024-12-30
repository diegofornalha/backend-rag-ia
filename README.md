# Backend RAG IA

Backend para processamento de IA usando RAG (Retrieval Augmented Generation).

## Deploy Status

O deploy é feito automaticamente no Render através de GitHub Actions quando há push na branch main.

Serviço: https://backend-rag-ia-r7gn.onrender.com

## Ambiente Docker

### ⚠️ Importante: Docker Local e CI/CD

O funcionamento correto do Docker localmente é crucial pois:

1. **Validação de Builds**:

   - Permite testar se o build funcionará no GitHub Actions e Render
   - Evita commits que quebrariam a pipeline de CI/CD
   - Economiza tempo detectando problemas antes do deploy

2. **Compatibilidade de Arquitetura**:

   - Garante que as dependências compiladas (como faiss-cpu) funcionem em diferentes arquiteturas
   - Essencial para Mac M1/M2 (ARM64) vs servidores (x86_64)

3. **Reprodutibilidade**:
   - Ambiente idêntico em desenvolvimento e produção
   - Evita o clássico "funciona na minha máquina"

### Comando Correto para Rodar

O comando que resolve os problemas de módulos não encontrados é:

```bash
docker run -p 10000:10000 -e PYTHONPATH=/app/backend-rag-ia backend:local uvicorn backend-rag-ia.main:app --host 0.0.0.0 --port 10000
```

Este comando é importante pois:

- Define o PYTHONPATH corretamente
- Aponta para o diretório correto do módulo main
- Configura o host e porta adequadamente

### Pré-requisitos

- Docker instalado
- Git instalado

### Construindo a imagem Docker

Para construir a imagem Docker localmente:

```bash
# Constrói a imagem com a tag 'backend:local'
docker build -t backend:local .
```

O processo de build pode demorar alguns minutos na primeira vez pois precisa:

- Baixar todas as dependências
- Compilar o faiss do código fonte (otimizado para sua arquitetura)
- Instalar todas as bibliotecas Python

### Rodando a aplicação

Para rodar a aplicação localmente:

```bash
# Roda o container expondo a porta 10000
docker run -p 10000:10000 -e PYTHONPATH=/app/backend-rag-ia backend:local uvicorn backend-rag-ia.main:app --host 0.0.0.0 --port 10000
```

A aplicação estará disponível em:

- http://localhost:10000

### Comandos úteis

```bash
# Lista containers em execução
docker ps

# Para um container específico
docker stop <CONTAINER_ID>

# Inicia um container parado
docker start <CONTAINER_ID>

# Remove um container
docker rm <CONTAINER_ID>

# Lista imagens disponíveis
docker images

# Remove uma imagem
docker rmi <IMAGE_ID>
```

### Estrutura do Dockerfile

O Dockerfile usa multi-stage build para otimizar o tamanho final da imagem:

1. Estágio de build (`builder`):

   - Usa Python 3.11 slim como base
   - Instala dependências de sistema necessárias
   - Cria ambiente virtual Python
   - Instala dependências Python em camadas para melhor cache
   - Compila o faiss do código fonte com otimizações para a arquitetura

2. Estágio final:
   - Usa Python 3.11 slim como base
   - Copia apenas o ambiente virtual do builder
   - Copia o código da aplicação
   - Configura variáveis de ambiente
   - Expõe a porta 10000

### Troubleshooting

1. Se encontrar erro de módulo não encontrado:

   - Verifique se o PYTHONPATH está configurado corretamente
   - O comando de run já inclui `-e PYTHONPATH=/app/backend-rag-ia`

2. Se precisar reconstruir a imagem:

   ```bash
   docker build --no-cache -t backend:local .
   ```

3. Para ver logs do container:

   ```bash
   docker logs <CONTAINER_ID>
   ```

4. Para entrar no container em execução:
   ```bash
   docker exec -it <CONTAINER_ID> /bin/bash
   ```

### Notas importantes

- A imagem é otimizada para sua arquitetura local (ARM64 para Mac M1/M2)
- O build pode ser mais lento na primeira vez devido à compilação do faiss
- Builds subsequentes serão mais rápidos devido ao cache do Docker
- O tamanho final da imagem é aproximadamente 4.25 GB devido às dependências de ML
