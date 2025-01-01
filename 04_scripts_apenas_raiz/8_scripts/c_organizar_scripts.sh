#!/bin/bash

cd scripts_apenas_raiz

# Criar diretórios para organização
mkdir -p busca          # Scripts relacionados à busca semântica
mkdir -p ambiente       # Scripts de configuração de ambiente
mkdir -p monitoramento  # Scripts de monitoramento
mkdir -p database       # Scripts relacionados ao banco de dados
mkdir -p ci            # Scripts de CI/CD e formatação
mkdir -p deploy        # Scripts de deploy e controle

# Scripts de busca semântica
mv testar_busca_semantica.py busca/
mv testar_busca_embeddings.py busca/
mv testar_busca_render.py busca/
mv testar_busca_supabase.py busca/
mv verificar_status_busca.py busca/
mv configurar_urls_busca.py busca/

# Scripts de ambiente
mv preparar_ambiente.py ambiente/
mv verificar_ambiente.py ambiente/
mv testar_configuracao.py ambiente/
mv testar_supabase.py ambiente/
mv testar_supabase_http.py ambiente/
mv instalar_hooks.py ambiente/

# Scripts de monitoramento
mv monitorar_docker.py monitoramento/
mv verificar_prod.py monitoramento/
mv gerar_relatorio_ruff.py monitoramento/

# Scripts de banco de dados
mv testar_base_conhecimento.py database/
mv executar_sql.py database/
mv testar_document_hash.py database/
mv inserir_documentos_teste.py database/
mv testar_upload_regras.py database/
mv listar_documentos.py database/
mv registrar_problema_e_indexar.py database/

# Scripts de CI
mv formatar.py ci/

# Scripts de deploy
mv controlar_render.py deploy/
mv controlar_ssh.sh deploy/
mv iniciar.sh deploy/

# Remover scripts duplicados ou obsoletos
rm -f testar_busca_supabase.py  # Funcionalidade já em testar_busca_semantica.py
rm -f testar_supabase_http.py   # Substituído por testar_supabase.py

echo "Scripts organizados com sucesso!" 