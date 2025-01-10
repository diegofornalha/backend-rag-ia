#!/bin/bash

# Carrega variáveis de ambiente
source .env

# Define variáveis padrão se não estiverem definidas
HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-10000}
ENVIRONMENT=${ENVIRONMENT:-"development"}

# Inicia a aplicação baseado no ambiente
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Iniciando em modo produção..."
    exec gunicorn -c gunicorn.conf.py backend_rag_ai.main:app
else
    echo "Iniciando em modo desenvolvimento..."
    exec uvicorn backend_rag_ai.main:app --host $HOST --port $PORT --reload
fi 