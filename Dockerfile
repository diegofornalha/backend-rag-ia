# Imagem base Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$PATH:/root/.local/bin" \
    PORT=10000 \
    OPERATION_MODE=render \
    IS_RENDER=true

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copia arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instala dependências
RUN poetry install --no-dev --no-root

# Copia o código da aplicação
COPY backend_rag_ia backend_rag_ia/

# Expõe a porta
EXPOSE $PORT

# Comando para iniciar a aplicação
CMD uvicorn backend_rag_ia.api.main:app --host 0.0.0.0 --port $PORT 