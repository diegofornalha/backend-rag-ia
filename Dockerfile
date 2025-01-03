# Imagem base Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="$PATH:/root/.local/bin" \
    PYTHONPATH=/app:$PYTHONPATH \
    PORT=10000 \
    HOST=0.0.0.0 \
    OPERATION_MODE=render \
    IS_RENDER=true

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY requirements.txt ./
COPY pyproject.toml ./
COPY poetry.lock ./

# Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia o código da aplicação
COPY backend_rag_ia /app/backend_rag_ia/
COPY 07_monitoring_apenas_raiz /app/07_monitoring_apenas_raiz/

# Verifica a instalação
RUN python -c "import backend_rag_ia.api.main"

# Expõe a porta
EXPOSE $PORT

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Comando para iniciar a aplicação
CMD ["sh", "-c", "uvicorn backend_rag_ia.api.main:app --host $HOST --port $PORT"]
