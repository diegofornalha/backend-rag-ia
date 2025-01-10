# Stage 1: Build
FROM python:3.11-slim as builder

# Configuração do ambiente de build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Adiciona poetry ao PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copia arquivos de dependência
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Instala dependências do projeto
RUN poetry install --no-dev --no-root

# Stage 2: Runtime
FROM python:3.11-slim as runtime

# Configuração do ambiente de runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    PATH="/opt/pysetup/.venv/bin:$PATH"

# Cria usuário não-root
RUN useradd --create-home appuser \
    && mkdir -p /app \
    && chown -R appuser:appuser /app

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copia ambiente virtual do builder
COPY --from=builder --chown=appuser:appuser $VENV_PATH $VENV_PATH

# Copia código da aplicação
WORKDIR /app
COPY --chown=appuser:appuser . .

# Configuração de usuário e portas
USER appuser
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "backend_rag_ai_py.main:app"] 