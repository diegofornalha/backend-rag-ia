#!/bin/bash

# Ativar ambiente virtual
source /opt/venv/bin/activate

# Variáveis de ambiente
export PYTHONPATH=/app
export PORT="${PORT:-10000}"
export HOST="${HOST:-0.0.0.0}"
export PYTHONUNBUFFERED=1

# Criar diretórios necessários
mkdir -p /app/logs
mkdir -p /app/cache

# Verificar permissões
chmod -R 755 /app/logs
chmod -R 755 /app/cache

# Configurar log do Gunicorn
export GUNICORN_CMD_ARGS="--capture-output --enable-stdio-inheritance"

# Iniciar aplicação com Gunicorn
exec gunicorn main:app \
    --bind $HOST:$PORT \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 300 \
    --graceful-timeout 120 \
    --keep-alive 5 \
    --log-level debug \
    --error-logfile /app/logs/error.log \
    --access-logfile /app/logs/access.log \
    --worker-tmp-dir /dev/shm \
    --preload 