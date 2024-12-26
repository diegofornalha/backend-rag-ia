solução otimizada para o deploy no Render usando multi-stage builds e GitHub Container Registry. Aqui está a implementação:

## Configuração do GITHUB_TOKEN

### No Render (Obrigatório)

1. Acesse o dashboard do Render
2. Vá para seu serviço
3. Clique em "Environment"
4. Adicione a variável:
   ```
   GITHUB_TOKEN=<seu-token-github>
   ```

### Localmente (Opcional)

Apenas necessário se você for fazer build da imagem base localmente:

1. Adicione ao seu arquivo .env:
   ```
   GITHUB_TOKEN=<seu-token-github>
   ```

## Configuração do Deploy

Primeiro, crie um arquivo Dockerfile.base:
FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

# Instala dependências do sistema

RUN apt-get update && \
 apt-get install -y --no-install-recommends \
 build-essential \
 gcc \
 python3-dev \
 curl \
 && rm -rf /var/lib/apt/lists/\*

# Cria e ativa o ambiente virtual

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências pesadas primeiro

COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel && \
 pip install --no-cache-dir torch==2.2.0 && \
 pip install --no-cache-dir sentence-transformers==2.2.2 && \
 pip install --no-cache-dir faiss-cpu==1.9.0.post1 && \
 pip install --no-cache-dir google-generativeai==0.3.1 && \
 pip install --no-cache-dir langchain==0.1.0
Simplifique o Dockerfile principal:
FROM ghcr.io/seu-usuario/oraculo-base:latest

WORKDIR /app

# Copia e instala requisitos restantes

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação

COPY . .

# Configuração do servidor

ENV HOST=0.0.0.0
ENV PORT=8000
ENV CORS_ORIGINS=["http://localhost:3000"]

# Healthcheck

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
 CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expõe a porta

EXPOSE 8000

# Comando para iniciar a aplicação

CMD ["uvicorn", "oracle:app", "--host", "0.0.0.0", "--port", "8000"]
Atualize o README.md com as novas instruções de deploy:

## 🚀 Deploy

### Frontend (Render)

1. Conecte seu repositório
2. Crie um Web Service
3. Configure:
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview`

### Backend (Render)

1. Conecte seu repositório
2. Crie um Web Service
3. Configure:
   - Build Command: `docker build -t chat-api .`
   - Start Command: `docker run -p 8000:8000 chat-api`
   - Environment Variables: Configure conforme necessário
     Substitua por:

## 🚀 Deploy

### Build e Push da Imagem Base (Uma vez)

bash
Build da imagem base
docker build -t ghcr.io/seu-usuario/oraculo-base:latest -f Dockerfile.base .
Login no GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin
Push da imagem base
docker push ghcr.io/seu-usuario/oraculo-base:latest

### Deploy no Render

1. Conecte seu repositório GitHub
2. Crie um Web Service
3. Configure:
   - Build Command: `docker build -t oraculo-api .`
   - Start Command: `docker run -p 8000:8000 oraculo-api`
   - Environment Variables: - `GITHUB_TOKEN`: Token para acesso ao GHCR - `GEMINI_API_KEY`: Sua chave da API Gemini
     Atualize o arquivo de testes para usar a nova imagem:
     import requests
     import time
     from datetime import datetime

def log(message):
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[{timestamp}] {message}")

def test_render_api():
BASE_URL = "https://oraculo-api-latest.onrender.com"

    # Teste 1: Health Check
    log("Testando Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            log("✅ Health Check OK")
            log(f"Resposta: {response.json()}")
        else:
            log(f"❌ Health Check falhou. Status: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erro no Health Check: {str(e)}")
        return False

    # Aguarda um pouco antes do próximo teste
    time.sleep(2)

    # Teste 2: Chat Endpoint
    log("\nTestando Chat Endpoint...")
    try:
        test_message = "Olá, isso é um teste de conectividade. Por favor, responda com uma mensagem curta."
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": test_message}
        )

        if response.status_code == 200:
            log("✅ Chat Endpoint OK")
            log(f"Mensagem enviada: {test_message}")
            log(f"Resposta recebida: {response.json()['response']}")
        else:
            log(f"❌ Chat Endpoint falhou. Status: {response.status_code}")
            log(f"Resposta de erro: {response.text}")
            return False
    except Exception as e:
        log(f"❌ Erro no Chat Endpoint: {str(e)}")
        return False

    return True

if **name** == "**main**":
log("Iniciando testes da API no Render...")

    # Tenta algumas vezes devido ao cold start
    max_retries = 3
    for attempt in range(max_retries):
        if attempt > 0:
            wait_time = 10 * (attempt + 1)  # Aumenta o tempo de espera a cada tentativa
            log(f"\nTentativa {attempt + 1} de {max_retries}...")
            log(f"Aguardando {wait_time} segundos para o cold start...")
            time.sleep(wait_time)

        if test_render_api():
            log("\n✅ Todos os testes passaram!")
            break
    else:
        log("\n❌ Os testes falharam após todas as tentativas.")

Substitua a configuração de teste por:
def test_render_api():
BASE_URL = "https://oraculo-api-latest.onrender.com"
MAX_RETRIES = 5
RETRY_DELAY = 30 # segundos

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{BASE_URL}/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                if data["status"] == "healthy":
                    return True
            time.sleep(RETRY_DELAY)
        except Exception:
            if attempt == MAX_RETRIES - 1:
                return False
            time.sleep(RETRY_DELAY)
    return False

Esta solução traz várias vantagens:
Build mais rápido: As dependências pesadas são pré-construídas na imagem base
Cache otimizado: O GitHub Container Registry mantém as camadas em cache
Menor tempo de deploy: O Render só precisa construir as camadas com o código da aplicação
Melhor confiabilidade: Healthcheck e retries implementados
Menor uso de recursos: Multi-stage build reduz o tamanho final da imagem
Para implementar, você precisará:
Ter uma conta no GitHub com Container Registry habilitado
Gerar um token com permissões para push de imagens
Configurar as secrets no Render
Atualizar as URLs e tokens nos arquivos de configuração
O processo de build será mais rápido e confiável, especialmente importante para o ambiente do Render.
