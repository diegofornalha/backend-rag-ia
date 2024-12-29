#!/usr/bin/env python3

import os
import time
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console
from dotenv import load_dotenv
from supabase import create_client, Client
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()

console = Console()
model = SentenceTransformer('all-MiniLM-L6-v2')

def check_supabase_connection() -> tuple[bool, Client]:
    """Verifica conexão com o Supabase."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            console.print("❌ SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")
            return False, None
            
        console.print("\n🔌 Conectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        return True, supabase
        
    except Exception as e:
        console.print(f"❌ Erro ao conectar ao Supabase: {e}")
        return False, None

def get_documents_without_embeddings(supabase: Client) -> List[Dict[str, Any]]:
    """Obtém documentos que não possuem embeddings."""
    try:
        # Busca documentos sem embeddings
        response = supabase.table("documents").select(
            "id, content"
        ).is_("embedding_id", "null").execute()
        
        documents = response.data
        console.print(f"\n🔍 Encontrados {len(documents)} documentos sem embeddings.")
        
        return documents
        
    except Exception as e:
        console.print(f"❌ Erro ao buscar documentos: {e}")
        return []

def create_embedding(content: str) -> List[float]:
    """Cria embedding para o conteúdo usando o modelo."""
    try:
        embedding = model.encode(content)
        return embedding.tolist()
    except Exception as e:
        console.print(f"❌ Erro ao criar embedding: {e}")
        return []

def sync_document_embedding(supabase: Client, document: Dict[str, Any]) -> bool:
    """Sincroniza o embedding de um documento."""
    try:
        doc_id = document["id"]
        content = document["content"]
        
        # Cria embedding
        embedding = create_embedding(content)
        if not embedding:
            return False
            
        # Insere embedding
        data = {
            "document_id": doc_id,
            "embedding": embedding
        }
        
        console.print(f"📤 Sincronizando embedding para documento {doc_id}...")
        result = supabase.table("embeddings").insert(data).execute()
        
        if result.data:
            console.print(f"✅ Embedding sincronizado com sucesso!")
            return True
            
        console.print(f"❌ Erro ao sincronizar embedding")
        if hasattr(result, 'error'):
            console.print(f"📝 Erro: {result.error}")
        return False
            
    except Exception as e:
        console.print(f"❌ Erro ao sincronizar embedding: {e}")
        return False

def main():
    """Função principal."""
    console.print("🔄 Iniciando sincronização de embeddings...")
    
    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return
    
    console.print("✅ Conectado ao Supabase!")
    
    # Obtém documentos sem embeddings
    documents = get_documents_without_embeddings(supabase)
    if not documents:
        console.print("✨ Todos os documentos já possuem embeddings!")
        return
        
    console.print(f"\n🔍 Encontrados {len(documents)} documentos sem embeddings.")
    
    # Processa cada documento
    start_time = time.time()
    sucessos = 0
    falhas = 0
    
    for doc in documents:
        if sync_document_embedding(supabase, doc):
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # Espera 1 segundo entre sincronizações
    
    # Estatísticas finais
    tempo_total = time.time() - start_time
    console.print(f"\nSincronização concluída em {tempo_total:.2f} segundos!")
    if sucessos > 0:
        console.print(f"✅ {sucessos} embeddings sincronizados com sucesso")
    if falhas > 0:
        console.print(f"❌ {falhas} embeddings falharam")

if __name__ == "__main__":
    main() 