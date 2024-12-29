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

# Copia e instala requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

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
ENV PORT=10000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Cria diretório para logs e cache
RUN mkdir -p /app/logs /app/cache \
    && chmod -R 755 /app/logs /app/cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/api/v1/health || exit 1

# Expõe a porta
EXPOSE 10000

# Script de inicialização
COPY ./scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Comando para iniciar a aplicação
CMD ["/app/start.sh"] 