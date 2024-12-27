#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
NC='\033[0m'

# Diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR"

# Função para verificar se o processo está rodando
check_process() {
    lsof -i :$1 >/dev/null 2>&1
}

# Mata processo na porta se existir
kill_port() {
    if check_process $1; then
        echo "Matando processo na porta $1..."
        lsof -ti :$1 | xargs kill -9
    fi
}

# Limpa portas que podem estar em uso
kill_port 5173  # Frontend Vite
kill_port 8000  # Backend

# Inicia o backend
echo -e "${GREEN}Iniciando Backend...${NC}"
cd "$BACKEND_DIR"
python3 main.py &

# Aguarda 5 segundos para o backend iniciar
sleep 5

# Inicia o frontend
echo -e "${GREEN}Iniciando Frontend...${NC}"
cd "$FRONTEND_DIR"
yarn dev

# Trap para matar todos os processos ao sair
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT 