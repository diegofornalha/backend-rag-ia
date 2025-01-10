#!/bin/bash
set -a; source .env; set +a; if [ "$ENVIRONMENT" = "production" ]; then echo "Iniciando em modo produção..."; exec gunicorn -c gunicorn.conf.py backend_rag_ia.main:app; else echo "Iniciando em modo desenvolvimento..."; exec uvicorn backend_rag_ia.main:app --host $HOST --port $PORT --reload; fi
