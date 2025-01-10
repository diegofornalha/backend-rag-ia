FROM python:3.11-slim as builder

# Instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar apenas os arquivos necessários para instalar as dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Estágio final
FROM python:3.11-slim

# Criar usuário não-root
RUN useradd --create-home appuser

WORKDIR /app

# Copiar apenas os pacotes Python necessários
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copiar o código da aplicação
COPY backend_rag_ai_py /app/backend_rag_ai_py/

# Mudar para o usuário não-root
USER appuser

# Expor a porta
EXPOSE 10000

# Comando para executar a aplicação
CMD ["uvicorn", "backend_rag_ai_py.main:app", "--host", "0.0.0.0", "--port", "10000"] 