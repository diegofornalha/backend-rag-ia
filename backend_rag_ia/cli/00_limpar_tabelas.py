#!/usr/bin/env python3

import os
from supabase import create_client, Client

def main():
    # Configuração do cliente Supabase
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    print("Iniciando limpeza das tabelas...")
    print(f"Conectado ao Supabase: {url}")
    
    try:
        # Busca embeddings existentes
        embeddings = supabase.table("02_embeddings_regras_geral") \
            .select("id") \
            .execute()
            
        total_embeddings = len(embeddings.data) if embeddings.data else 0
        print(f"\nEncontrados {total_embeddings} embeddings para deletar")
        
        # Deleta embeddings
        if total_embeddings > 0:
            supabase.table("02_embeddings_regras_geral").delete().eq("id", embeddings.data[0]["id"]).execute()
            print("✓ Embeddings deletados com sucesso")
        
        # Busca documentos existentes
        documents = supabase.table("01_base_conhecimento_regras_geral") \
            .select("id") \
            .execute()
            
        total_documents = len(documents.data) if documents.data else 0
        print(f"\nEncontrados {total_documents} documentos para deletar")
        
        # Deleta documentos
        if total_documents > 0:
            supabase.table("01_base_conhecimento_regras_geral").delete().eq("id", documents.data[0]["id"]).execute()
            print("✓ Documentos deletados com sucesso")
            
        print("\nLimpeza concluída com sucesso!")
        
    except Exception as e:
        print(f"\nErro durante a limpeza: {str(e)}")

if __name__ == "__main__":
    main() 