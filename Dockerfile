FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpq-dev \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos do projeto
COPY requirements.txt .
COPY main.py .
COPY backend_rag_ia ./backend_rag_ia

# Configura ambiente virtual e instala dependências Python
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Atualiza pip e instala ferramentas de build
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala pgvector primeiro para garantir suas dependências
RUN pip install --no-cache-dir pgvector==0.2.4

# Instala as demais dependências
RUN pip install --no-cache-dir -r requirements.txt

# Define variáveis de ambiente
ENV PYTHONPATH=/app:/app/backend_rag_ia
ENV PYTHON_VERSION=3.11
ENV HOST=0.0.0.0
ENV PORT=10000

# Expõe a porta
EXPOSE 10000

# Comando para executar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"] 