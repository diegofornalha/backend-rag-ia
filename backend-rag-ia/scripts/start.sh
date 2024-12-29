#!/bin/bash

# Ativa o ambiente virtual
source /opt/venv/bin/activate

# Executa as migrações se necessário
# python manage.py migrate

# Inicia o servidor
uvicorn main:app --host 0.0.0.0 --port $PORT 