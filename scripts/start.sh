#!/bin/bash

# Função para log
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S %Z')] $1"
}

# Ativar ambiente virtual
source /opt/venv/bin/activate

# Variáveis de ambiente
export PYTHONPATH=/app
export PORT="${PORT:-8000}"
export HOST="${HOST:-0.0.0.0}"
export WORKERS="${WORKERS:-4}"

log "Iniciando aplicação..."

# Verificar variáveis de ambiente
log "Verificando variáveis de ambiente..."
if [ -z "$SUPABASE_URL" ]; then
    log "ERRO: Variável de ambiente SUPABASE_URL não está definida"
    exit 1
fi
log "✓ Variáveis de ambiente verificadas"

# Verificar estrutura de arquivos
log "Verificando estrutura de arquivos..."
if [ ! -f "/app/oracle.py" ]; then
    log "ERRO: Arquivo oracle.py não encontrado"
    exit 1
fi
log "✓ Estrutura de arquivos verificada"

# Verificar permissões
log "Verificando permissões..."
mkdir -p /app/logs /app/cache
chmod -R 755 /app/logs /app/cache
log "✓ Permissões verificadas"

# Verificar dependências
log "Verificando dependências..."
pip check
log "✓ Dependências verificadas"

# Iniciar servidor
log "Iniciando servidor..."
exec gunicorn oracle:app \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level ${LOG_LEVEL:-info} \
    --reload 