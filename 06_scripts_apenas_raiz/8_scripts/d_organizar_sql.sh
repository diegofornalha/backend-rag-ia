#!/bin/bash

# Entra no diretório sql
cd sql

# Arquivos a serem removidos (duplicados ou obsoletos)
rm -f move_to_rag.sql          # Obsoleto - já foi migrado
rm -f rename_table.sql         # Obsoleto - já foi renomeado
rm -f reverter_nomes.sql       # Obsoleto - já foi revertido
rm -f limpar_tabelas_antigas.sql # Duplicado - já temos limpar_referencias_antigas.sql
rm -f setup_security_all.sql   # Consolidado em setup_security.sql
rm -f setup_functions_security.sql # Consolidado em setup_security.sql

# Move arquivos de setup (essenciais)
mv init.sql setup/
mv setup_embeddings.sql setup/
mv setup_search.sql setup/
mv base_conhecimento_geral.sql setup/

# Move arquivos de manutenção (essenciais)
mv setup_maintenance.sql maintenance/
mv analyze_tables.sql maintenance/
mv limpar_referencias_antigas.sql maintenance/

# Move arquivos de segurança (essenciais)
mv setup_security.sql security/

# Move arquivos de migração (essenciais)
mv move_schema.sql migrations/
mv reorganize_schemas.sql migrations/
mv separar_embeddings.sql migrations/
mv adicionar_document_hash.sql migrations/

echo "Arquivos organizados e limpos com sucesso!" 