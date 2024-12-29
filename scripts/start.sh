#!/bin/bash

# Ativar ambiente virtual
source /opt/venv/bin/activate

# Variáveis de ambiente
export PYTHONPATH=/app
export PORT="${PORT:-10000}"
export HOST="${HOST:-0.0.0.0}"

# Criar diretórios necessários
mkdir -p /app/logs
mkdir -p /app/cache

# Verificar permissões
chmod -R 755 /app/logs
chmod -R 755 /app/cache

# Iniciar aplicação com Gunicorn
exec gunicorn main:app \
    --bind $HOST:$PORT \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --reload 