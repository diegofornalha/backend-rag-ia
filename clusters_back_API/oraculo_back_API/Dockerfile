# Use a imagem base Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos e .env
COPY ./clusters_back_API/oraculo_back_API/requirements.txt .
COPY ./clusters_back_API/oraculo_back_API/.env .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY ./clusters_back_API/oraculo_back_API .

# Expõe a porta (usando variável de ambiente do Render)
ENV PORT=10000
EXPOSE ${PORT}

# Configurações do Uvicorn
ENV WORKERS=4
ENV TIMEOUT_KEEP_ALIVE=300

# Define o comando para iniciar a aplicação com mais recursos
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS} --timeout-keep-alive ${TIMEOUT_KEEP_ALIVE} --limit-concurrency 50"] 