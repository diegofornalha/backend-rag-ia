#!/bin/bash

# Criar diretório principal se não existir
mkdir -p testes_apenas_raiz

# Criar estrutura de diretórios
mkdir -p testes_apenas_raiz/unit          # Testes unitários
mkdir -p testes_apenas_raiz/integration   # Testes de integração
mkdir -p testes_apenas_raiz/monitoring    # Testes de monitoramento
mkdir -p testes_apenas_raiz/fixtures      # Dados de teste
mkdir -p testes_apenas_raiz/utils         # Utilitários de teste

# Mover arquivos de teste do backend_rag_ia
find backend_rag_ia -type f -name "test_*.py" -exec mv {} testes_apenas_raiz/ \;
find backend_rag_ia -type f -name "*_test.py" -exec mv {} testes_apenas_raiz/ \;

# Organizar testes por categoria
mv testes_apenas_raiz/test_*_unit.py testes_apenas_raiz/unit/
mv testes_apenas_raiz/test_*_integration.py testes_apenas_raiz/integration/
mv testes_apenas_raiz/test_*_monitoring.py testes_apenas_raiz/monitoring/

# Mover arquivos de configuração de teste
mv testes_apenas_raiz/conftest.py testes_apenas_raiz/
mv testes_apenas_raiz/pytest.ini testes_apenas_raiz/
mv testes_apenas_raiz/test_data.json testes_apenas_raiz/fixtures/

# Remover diretórios vazios
find backend_rag_ia -type d -empty -delete

echo "Testes organizados com sucesso!" 