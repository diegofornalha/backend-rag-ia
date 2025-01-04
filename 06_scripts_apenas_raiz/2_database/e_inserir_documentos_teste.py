"""Script para inserir documentos de teste no Supabase."""

import os
from datetime import datetime
from supabase import create_client

def inserir_documentos_teste():
    """Insere documentos de teste no Supabase."""
    # Verifica variáveis de ambiente
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: Variáveis SUPABASE_URL e SUPABASE_KEY não definidas")
        return False
        
    try:
        # Conecta ao Supabase
        supabase = create_client(url, key)
        
        # Documentos de teste
        documentos = [
            {
                "titulo": "Regra de Negócio 1",
                "conteudo": "Exemplo de regra de negócio para teste",
                "tipo": "regra",
                "status": "ativo",
                "criado_em": datetime.now().isoformat(),
                "atualizado_em": datetime.now().isoformat()
            },
            {
                "titulo": "Política 1",
                "conteudo": "Exemplo de política para teste",
                "tipo": "politica",
                "status": "ativo",
                "criado_em": datetime.now().isoformat(),
                "atualizado_em": datetime.now().isoformat()
            }
        ]
        
        # Insere documentos
        for doc in documentos:
            response = supabase.client.table("rag.documentos").insert(doc).execute()
            print(f"✅ Documento inserido: {doc['titulo']}")
            
        print("✨ Documentos de teste inseridos com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir documentos: {e}")
        return False
        
if __name__ == "__main__":
    inserir_documentos_teste() 