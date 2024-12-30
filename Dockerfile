FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY requirements.txt .
COPY main.py .
COPY backend-rag-ia ./backend-rag-ia

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Define variáveis de ambiente
ENV PYTHONPATH=/app

# Expõe a porta
EXPOSE 10000

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"] 