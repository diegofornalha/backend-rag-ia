#!/bin/bash

# Ativa o ambiente virtual
source /opt/venv/bin/activate

# Executa as migrações do banco de dados (se necessário)
# python manage.py migrate

# Inicia o servidor Gunicorn
exec gunicorn main:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
