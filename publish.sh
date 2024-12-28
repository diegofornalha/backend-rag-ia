#!/bin/bash

# Limpa diretório dist anterior se existir
rm -rf dist/*

# Gera os arquivos de distribuição
python setup.py sdist bdist_wheel

# Faz upload para o PyPI
twine upload dist/*

echo "Pacote publicado com sucesso!"
