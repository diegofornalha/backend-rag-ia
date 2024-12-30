# Backend RAG IA

Backend para processamento de IA usando RAG (Retrieval Augmented Generation).

## Diferenciais do Sistema RAG

### 🚀 Características Principais

1. **Arquitetura Otimizada**:

   - Multi-stage Docker para build eficiente
   - Suporte nativo a múltiplas arquiteturas (ARM64/AMD64)
   - Integração contínua automatizada (GitHub Actions + Render)

2. **Stack Tecnológica Moderna**:

   - FastAPI para alta performance e documentação automática
   - Supabase+pgvector para busca semântica eficiente
   - Sentence Transformers para embeddings de alta qualidade
   - Hugging Face Transformers para processamento de linguagem natural

3. **Escalabilidade e Performance**:

   - Cache inteligente de embeddings
   - Processamento assíncrono com FastAPI
   - Otimização de memória com pgvector
   - Compilação nativa de dependências críticas

4. **Segurança e Robustez**:
   - Testes automatizados de dependências
   - Verificação de vulnerabilidades no CI/CD
   - Monitoramento de deploys em tempo real
   - Rollback automático em caso de falhas

### 🔄 Pipeline de Processamento

1. **Entrada**:

   - Recebe textos em formato livre
   - Suporta múltiplos formatos de entrada
   - Processamento de lotes (batch) eficiente

2. **Processamento**:

   - Geração de embeddings otimizada
   - Busca semântica com Supabase+pgvector
   - Ranqueamento inteligente de resultados
   - Contextualização automática

3. **Saída**:
   - Respostas estruturadas em JSON
   - Métricas de confiança
   - Rastreabilidade das fontes
   - Cache de resultados frequentes

### 🛠️ Facilidade de Uso

1. **Deploy Simplificado**:

   - Um comando para build multi-plataforma
   - Deploy automático no Render
   - Monitoramento integrado
   - Logs estruturados

2. **Documentação Clara**:

   - API auto-documentada com Swagger
   - Exemplos práticos de uso
   - Guias de troubleshooting
   - Boas práticas documentadas

3. **Manutenibilidade**:
   - Código modular e bem organizado
   - Dependências versionadas
   - Atualizações automáticas via Dependabot
   - Testes automatizados

## Deploy Status

O deploy é feito automaticamente no Render através de GitHub Actions quando há push na branch main.

Serviço: https://backend-rag-ia-r7gn.onrender.com

### Variáveis de Ambiente do Render

Para gerenciar o servidor via API, configure:

```bash
export RENDER_API_KEY='rnd_6SveVNcKW0cCS2OT6VwY8gRDON5h'
export RENDER_SERVICE_ID='srv-ctoq9hdds78s73ctpp70'
```

Estas variáveis são necessárias para:

- Monitorar status do servidor
- Reiniciar o servidor
- Verificar logs de deploy
- Forçar uso da imagem Docker correta (linux/amd64)

## Ambiente Docker

### ⚠️ Importante: Docker Local e CI/CD

O funcionamento correto do Docker localmente é crucial pois:

1. **Validação de Builds**:

   - Permite testar se o build funcionará no GitHub Actions e Render
   - Evita commits que quebrariam a pipeline de CI/CD
   - Economiza tempo detectando problemas antes do deploy

2. **Compatibilidade de Arquitetura**:

   - Garante que as dependências funcionem em diferentes arquiteturas
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
- Instalar todas as bibliotecas Python
- Configurar o ambiente

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

### Docker Hub

Para publicar a imagem no Docker Hub:

```bash
# Login no Docker Hub (username: fornalha)
docker login

# Taguear a imagem para o Docker Hub
docker tag backend:local fornalha/backend:latest

# Enviar para o Docker Hub
docker push fornalha/backend:latest
```

> Nota: Embora seja possível publicar no Docker Hub, não é necessário para o deploy no Render, que já faz o build automaticamente a partir do GitHub.

### Notas importantes

- A imagem é otimizada para sua arquitetura local (ARM64 para Mac M1/M2)
- O build pode ser mais lento na primeira vez devido à compilação do faiss
- Builds subsequentes serão mais rápidos devido ao cache do Docker
- O tamanho final da imagem é aproximadamente 4.25 GB devido às dependências de ML

## Multi-plataforma Docker

### Importância do Suporte Multi-plataforma

Este projeto utiliza uma configuração Docker multi-plataforma para garantir compatibilidade entre diferentes arquiteturas:

- **Desenvolvimento Local**: Principalmente em Macs com Apple Silicon (ARM64)
- **Produção/CI**: Servidores e GitHub Actions (AMD64)

A falta de suporte multi-plataforma pode causar vários problemas:

- ❌ Falhas no CI/CD
- ❌ Incompatibilidade entre desenvolvimento e produção
- ❌ Erros de compilação de dependências nativas (como faiss-cpu)

### Como Construir para Múltiplas Plataformas

```bash
# Configurar builder multi-plataforma
docker buildx create --use --name multiarch-builder

# Construir e publicar para múltiplas plataformas
docker buildx build --platform linux/amd64,linux/arm64 -t fornalha/backend:latest --push .
```

### Verificar Suporte Multi-plataforma

```bash
# Verificar plataformas suportadas pela imagem
docker manifest inspect fornalha/backend:latest

# Pull específico para sua plataforma
docker pull --platform linux/amd64 fornalha/backend:latest  # Para AMD64
docker pull --platform linux/arm64 fornalha/backend:latest  # Para ARM64
```

### Dicas Importantes

1. **Desenvolvimento Local**:

   - Em Macs com M1/M2, você está usando ARM64
   - Use `--platform` se precisar testar outras arquiteturas

2. **CI/CD**:

   - GitHub Actions usa AMD64 por padrão
   - Render e maioria dos serviços cloud usam AMD64

3. **Dependências Nativas**:
   - Algumas dependências Python precisam ser compiladas
   - Importante testar em todas as plataformas suportadas
   - Usar `--platform=$BUILDPLATFORM` e `--platform=$TARGETPLATFORM` no Dockerfile

## Acesso SSH ao Render

### Configuração do SSH

Para acessar e gerenciar o servidor diretamente via SSH:

1. **Gerar chave SSH**:

   ```bash
   ssh-keygen -t ed25519 -C "seu@email.com"
   ```

2. **Copiar chave pública**:

   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. **Adicionar no Render**:
   - Acesse: https://dashboard.render.com/ssh-keys
   - Cole sua chave pública

### Comandos SSH Úteis

1. **Conectar ao servidor**:

   ```bash
   ssh render@ssh.render.com
   ```

2. **Reiniciar servidor sem usar builds**:

   ```bash
   # Acessar diretório do projeto
   cd /opt/render/project/src

   # Atualizar imagem Docker
   docker pull fornalha/backend:latest

   # Parar containers em execução
   docker stop $(docker ps -q)

   # Iniciar novo container
   docker run -d -p 10000:10000 fornalha/backend:latest
   ```

3. **Verificar logs**:

   ```bash
   # Ver logs do container
   docker logs $(docker ps -q)

   # Seguir logs em tempo real
   docker logs -f $(docker ps -q)
   ```

### Vantagens do SSH

1. **Contorna limites do Render**:

   - Evita o limite de builds
   - Permite reiniciar sem consumir créditos
   - Mais rápido que rebuild completo

2. **Acesso direto**:

   - Debug em tempo real
   - Verificação de logs
   - Gerenciamento de containers

3. **Flexibilidade**:
   - Comandos Docker diretos
   - Verificação de sistema
   - Troubleshooting avançado

### Troubleshooting via SSH

1. **Problemas de memória**:

   ```bash
   # Verificar uso de memória
   docker stats

   # Limpar containers não utilizados
   docker system prune -f
   ```

2. **Problemas de rede**:

   ```bash
   # Verificar portas em uso
   netstat -tulpn

   # Testar conexão interna
   curl localhost:10000
   ```

3. **Logs e Debug**:

   ```bash
   # Ver logs detalhados
   docker logs --tail 100 $(docker ps -q)

   # Entrar no container
   docker exec -it $(docker ps -q) /bin/bash
   ```

## Desenvolvimento

1. Instale as dependências de desenvolvimento:

```bash
pip install -r requirements.txt
```

2. Configure os hooks de git:

```bash
python scripts_apenas_raiz/instalar_hooks.py
```

3. Execute os testes:

```bash
pytest
```

4. Verifique a qualidade do código:

```bash
python scripts_apenas_raiz/verificar_codigo.py
```

> **Nota**: A verificação de código é executada automaticamente antes de cada commit e durante o CI/CD.

### Padrões de Código

Este projeto usa o Ruff para garantir a qualidade do código. As verificações incluem:

- Formatação de código (PEP 8)
- Organização de imports
- Detecção de código não utilizado
- Verificações de segurança
- Otimizações de performance

Para mais detalhes, consulte a configuração em `pyproject.toml`.
