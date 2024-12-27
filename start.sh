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

# Define variáveis de ambiente do Gunicorn otimizadas para 2GB RAM
export GUNICORN_CMD_ARGS="--capture-output --enable-stdio-inheritance"
export WEB_CONCURRENCY=2
export PYTHON_MAX_MEMORY=1536  # 1.5GB para dar margem de segurança

# Inicia o servidor com configuração otimizada para plano Standard
exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --workers=2 \
    --threads=2 \
    --worker-connections 8 \
    --backlog 16 \
    --timeout 240 \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --max-requests 100 \
    --max-requests-jitter 20 \
    --worker-tmp-dir /dev/shm \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --log-file - 