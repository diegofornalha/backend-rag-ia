#!/bin/bash

echo "Iniciando aplicação..."

# Verifica variáveis de ambiente obrigatórias
required_vars=(
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "GEMINI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Erro: Variável de ambiente $var não está definida"
        exit 1
    fi
done

echo "Variáveis de ambiente verificadas"

# Verifica se o arquivo principal existe
if [ ! -f "oracle.py" ]; then
    echo "Erro: Arquivo oracle.py não encontrado"
    exit 1
fi

echo "Arquivos verificados"

# Tenta iniciar o servidor
echo "Iniciando servidor..."
exec uvicorn oracle:app --host 0.0.0.0 --port 8000 --log-level info 