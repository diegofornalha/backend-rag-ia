# Stage 1: Build
FROM python:3.11-slim as builder

# Configuração do ambiente de build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação e copia todo o código
WORKDIR /app/backend-rag-ai
COPY backend-rag-ai/ .

# Instala dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Configuração do ambiente de runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=10000

# Cria usuário não-root
RUN useradd --create-home appuser \
    && mkdir -p /app/backend-rag-ai \
    && chown -R appuser:appuser /app

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências e código
WORKDIR /app/backend-rag-ai
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --chown=appuser:appuser backend-rag-ai/ .

# Configuração de usuário e portas
USER appuser
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Comando de inicialização
CMD uvicorn backend_rag_ai_py.main:app --host 0.0.0.0 --port $PORT 