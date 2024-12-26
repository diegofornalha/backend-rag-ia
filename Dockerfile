# Build do Frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Copia arquivos do frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Build do Backend
FROM --platform=linux/amd64 python:3.12-slim AS backend-builder

WORKDIR /app

# Argumentos de build
ARG ENV=prod
ARG PORT=3000
ARG PYTHON_VERSION=3.12.0

# Variáveis de ambiente
ENV PORT=${PORT}
ENV PYTHON_VERSION=${PYTHON_VERSION}
ENV CORS_ORIGINS="http://localhost:3000,http://localhost:5173,https://oraculo-asimov.vercel.app"

# Instala curl para healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copia os arquivos essenciais primeiro
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto dos arquivos
COPY . .

# Copia os arquivos do frontend buildado
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expõe a porta
EXPOSE ${PORT}

# Define o comando baseado no ambiente
CMD if [ "$ENV" = "test" ]; then \
    python -m pytest tests/ --verbose; \
    else \
    uvicorn oracle:app --host 0.0.0.0 --port ${PORT} --workers 4; \
    fi 