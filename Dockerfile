FROM --platform=$BUILDPLATFORM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema e curl para healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Cria e ativa o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Atualiza pip e instala todas as dependências de uma vez
RUN pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Configuração do servidor
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cria diretório para logs e cache
RUN mkdir -p /app/logs /app/cache && \
    chmod -R 755 /app/logs /app/cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expõe a porta
EXPOSE 8000

# Script de inicialização
COPY scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Comando para iniciar a aplicação
CMD ["/app/start.sh"] 