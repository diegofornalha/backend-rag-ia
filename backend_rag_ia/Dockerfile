# Imagem base Python
FROM python:3.11-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="$PATH:/home/app/.local/bin" \
    PORT=10000 \
    OPERATION_MODE=render \
    IS_RENDER=true

# Cria usuário não-root
RUN groupadd -r app && useradd -r -g app app

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Define permissões e instala dependências
RUN chown -R app:app /app && \
    pip install --user --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY --chown=app:app . .

# Muda para o usuário não-root
USER app

# Expõe a porta
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "backend_rag_ia.main:app", "--host", "0.0.0.0", "--port", "10000"]
