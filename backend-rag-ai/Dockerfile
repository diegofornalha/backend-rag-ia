FROM python:3.11-slim as builder

# Instalar dependências de build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Imagem final
FROM python:3.11-slim

# Criar usuário não-root
RUN useradd --create-home appuser

WORKDIR /app

# Copiar dependências do builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copiar código da aplicação
COPY . .

# Definir usuário não-root
USER appuser

# Expor porta
EXPOSE 10000

# Comando para executar a aplicação
CMD ["uvicorn", "backend_rag_ai_py.main:app", "--host", "0.0.0.0", "--port", "10000"] 