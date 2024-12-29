# Imagem base para build
FROM python:3.11-slim as builder

# Diretório de trabalho
WORKDIR /app

# Cria e ativa ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Imagem final
FROM python:3.11-slim

# Copia ambiente virtual do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Diretório de trabalho
WORKDIR /app

# Copia código fonte
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/logs /app/cache \
    && chmod -R 755 /app/logs /app/cache

# Script de inicialização
COPY scripts/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Comando de inicialização
CMD ["/app/start.sh"] 