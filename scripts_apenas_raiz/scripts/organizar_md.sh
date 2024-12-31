#!/bin/bash

# Entra no diretório regras_md
cd regras_md

# Cria diretórios principais se não existirem
mkdir -p core          # Regras fundamentais do projeto
mkdir -p database      # Regras relacionadas ao banco de dados
mkdir -p deployment    # Regras de implantação e ambiente
mkdir -p development   # Regras de desenvolvimento
mkdir -p monitoring    # Regras de monitoramento e logs

# Move arquivos principais/core
mv PROJECT_RULES.md core/
mv REGRAS_PRINCIPAIS.md core/
mv REGRAS_DOCUMENTACAO.md core/
mv REGRAS_ARQUIVOS_CRITICOS.md core/
mv REGRAS_VERIFICACAO_DUPLA.md core/

# Move arquivos relacionados ao banco de dados
mv REGRAS_SQL_EDITOR_SUPABASE.md database/
mv REGRAS_SUPABASE.md database/
mv ESTRUTURA_TABELAS.md database/
mv PROBLEMAS_CONHECIDOS.md database/

# Move arquivos de implantação
mv REGRAS_RENDER.md deployment/
mv REGRAS_DOCKER.md deployment/
mv REGRAS_DEPENDENCIAS.md deployment/
mv REGRAS_FLUXO_GITHUB.md deployment/

# Move arquivos de desenvolvimento
mv REGRAS_API.md development/
mv REGRAS_BUSCA_SEMANTICA.md development/
mv REGRAS_RESOLVER_DESAFIOS.md development/
mv REGRAS_RUFF.md development/

# Move arquivos de monitoramento
mv REGRAS_MONITORAMENTO.md monitoring/
mv REGRAS_LOGS.md monitoring/

# Remove diretórios vazios antigos
rm -rf api busca desenvolvimento docker exemplos problemas

echo "Arquivos MD organizados com sucesso!" 