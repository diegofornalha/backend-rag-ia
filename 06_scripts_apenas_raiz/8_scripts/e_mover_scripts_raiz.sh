#!/bin/bash

# Criar diretórios se não existirem
mkdir -p scripts_apenas_raiz
mkdir -p scripts_apenas_raiz/scripts

# Mover scripts da raiz para scripts_apenas_raiz
find . -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" -o -name "*.json" \) ! -name "mover_scripts_raiz.sh" -exec mv {} scripts_apenas_raiz/ \;

# Mover scripts do backend_rag_ia para scripts_apenas_raiz
find backend_rag_ia -maxdepth 1 -type f \( -name "*.py" -o -name "*.sh" -o -name "*.json" \) ! -name "__init__.py" -exec mv {} scripts_apenas_raiz/ \;

# Mover scripts organizacionais
mv scripts_apenas_raiz/organizar_*.sh scripts_apenas_raiz/scripts/
mv scripts_apenas_raiz/limpar_*.sh scripts_apenas_raiz/scripts/

echo "Scripts movidos para scripts_apenas_raiz com sucesso!" 