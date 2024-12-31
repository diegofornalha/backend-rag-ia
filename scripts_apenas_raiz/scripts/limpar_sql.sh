#!/bin/bash

cd sql

# Removendo arquivos obsoletos/duplicados do setup
cd setup
rm -f 00_setup_exec_sql.sql    # Obsoleto - função já incorporada
rm -f setup_metrics.sql        # Funcionalidades já incorporadas em outros arquivos
cd ..

# Removendo arquivos obsoletos/duplicados da maintenance
cd maintenance
rm -f limpar_tabelas_antigas.sql  # Duplicado do limpar_referencias_antigas.sql
cd ..

# Removendo arquivos obsoletos/duplicados da security
cd security
rm -f setup_security_all.sql      # Consolidado em setup_security.sql
rm -f setup_functions_security.sql # Consolidado em setup_security.sql
cd ..

# Removendo arquivos obsoletos/duplicados das migrations
cd migrations
rm -f move_to_rag.sql          # Obsoleto - migração já realizada
rm -f rename_table.sql         # Obsoleto - renomeação já realizada
rm -f reverter_nomes.sql       # Obsoleto - reversão já realizada
cd ..

echo "Arquivos duplicados e obsoletos removidos com sucesso!" 