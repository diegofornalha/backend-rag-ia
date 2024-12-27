#!/bin/bash

# Verifica variáveis de ambiente necessárias
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY não está definida"
    exit 1
fi

if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "Error: SUPABASE_URL ou SUPABASE_KEY não estão definidas"
    exit 1
fi

# Verifica se o diretório models existe
if [ ! -d "models" ]; then
    echo "Error: Diretório 'models' não encontrado"
    exit 1
fi

# Inicia o servidor com Gunicorn
gunicorn main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --worker-tmp-dir /dev/shm \
    --max-requests 1000 \
    --max-requests-jitter 50 