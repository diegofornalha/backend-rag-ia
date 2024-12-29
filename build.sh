#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala dependências
pip install -r requirements.txt

# Coleta arquivos estáticos (se necessário)
# python manage.py collectstatic --no-input

# Executa migrações (se necessário)
# python manage.py migrate

# Configurações adicionais
export PORT=10000
export HOST=0.0.0.0
