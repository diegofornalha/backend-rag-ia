#!/bin/bash

set -e  # Sai em caso de erro

echo "[$(date)] Iniciando aplicação..."

# Função para log
log() {
    echo "[$(date)] $1"
}

# Verifica variáveis de ambiente obrigatórias
required_vars=(
    "SUPABASE_URL"
    "SUPABASE_KEY"
    "GEMINI_API_KEY"
)

log "Verificando variáveis de ambiente..."
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        log "ERRO: Variável de ambiente $var não está definida"
        exit 1
    fi
done
log "✓ Variáveis de ambiente verificadas"

# Verifica estrutura de arquivos
log "Verificando estrutura de arquivos..."
required_files=(
    "oracle.py"
    "requirements.txt"
    "api/routes.py"
    "services/vector_store.py"
    "services/supabase_client.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        log "ERRO: Arquivo $file não encontrado"
        ls -la $(dirname "$file")
        exit 1
    fi
done
log "✓ Estrutura de arquivos verificada"

# Verifica permissões
log "Verificando permissões..."
if [ ! -x "$(command -v python)" ]; then
    log "ERRO: Python não está instalado ou não tem permissão de execução"
    exit 1
fi
log "✓ Permissões verificadas"

# Verifica instalação de dependências
log "Verificando dependências..."
if ! pip list | grep -q "fastapi"; then
    log "ERRO: Dependências não estão instaladas corretamente"
    pip list
    exit 1
fi
log "✓ Dependências verificadas"

# Inicia o servidor
log "Iniciando servidor..."
exec uvicorn oracle:app --host 0.0.0.0 --port 8000 --log-level info 