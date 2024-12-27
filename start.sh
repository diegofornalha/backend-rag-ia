#!/bin/bash

# Verifica se as variáveis de ambiente necessárias estão definidas
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ SUPABASE_URL não está definida"
    exit 1
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "❌ SUPABASE_KEY não está definida"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY não está definida"
    exit 1
fi

# Verifica se o diretório documents existe
if [ ! -d "documents" ]; then
    echo "❌ Diretório 'documents' não encontrado"
    exit 1
fi

# Verifica se os arquivos necessários existem
if [ ! -f "oracle.py" ]; then
    echo "❌ Arquivo 'oracle.py' não encontrado"
    exit 1
fi

# Inicia o servidor
echo "🚀 Iniciando servidor..."
gunicorn oracle:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --timeout 300 --max-requests 250 --worker-connections 20 --graceful-timeout 120 --keep-alive 65 