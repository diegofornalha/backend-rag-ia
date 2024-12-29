# Estágio de construção
FROM python:3.12-slim as builder

WORKDIR /app

# Instala dependências essenciais
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria e ativa o ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências Python em camadas para melhor cache
COPY requirements.txt .
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -U pip setuptools wheel

# Instala primeiro as dependências base
RUN . /opt/venv/bin/activate && pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-dotenv==1.0.0 \
    gunicorn>=22.0.0 \
    pydantic==2.5.2 \
    "httpx>=0.24.0,<0.26.0"

# Depois instala as dependências ML que são mais pesadas
RUN . /opt/venv/bin/activate && pip install --no-cache-dir \
    "torch>=2.2.0" \
    "transformers==4.35.0" \
    "sentence-transformers==2.2.2" \
    "faiss-cpu==1.7.4"

# Por fim, instala o resto das dependências
RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

# Estágio final
FROM python:3.12-slim

WORKDIR /app

# Copia o ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala apenas o curl para healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copia o código da aplicação
COPY . .

# Configuração do servidor
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cria diretório para logs e cache
RUN mkdir -p /app/logs /app/cache \
    && chmod -R 755 /app/logs /app/cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expõe a porta
EXPOSE 8000

# Script de inicialização
COPY ./scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Comando para iniciar a aplicação
CMD ["/app/start.sh"] 