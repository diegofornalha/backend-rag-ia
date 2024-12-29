#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Verifica variáveis de ambiente necessárias
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}❌ SUPABASE_URL e SUPABASE_KEY são obrigatórios${NC}"
    exit 1
fi

# Ativa ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Inicia o servidor
echo -e "${GREEN}🚀 Iniciando Oráculo API...${NC}"
uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-10000} --workers ${WORKERS:-4} 