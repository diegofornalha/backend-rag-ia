#!/usr/bin/env python3

import os
import json
import time
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from dotenv import load_dotenv
from supabase import create_client, Client
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

def convert_document_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Converte o formato do documento para o formato esperado pela API."""
    # Combina os metadados globais com os metadados específicos do documento
    metadata = {
        **data["metadata_global"],
        **data["document"]["metadata"]
    }
    
    # Retorna no formato esperado
    return {
        "content": data["document"]["content"],
        "metadata": metadata
    }

def create_embedding(content: str) -> list[float]:
    """Cria embedding para o conteúdo usando o modelo."""
    try:
        embedding = model.encode(content)
        return embedding.tolist()
    except Exception as e:
        console.print(f"❌ Erro ao criar embedding: {e}")
        return []

def upload_document(supabase: Client, file_path: str) -> bool:
    """Faz upload de um documento para o Supabase."""
    try:
        # Carrega o documento
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Converte para o formato esperado
        document = convert_document_format(data)
        
        # Envia para o Supabase
        console.print(f"📤 Enviando {file_path}...")
        result = supabase.table("documents").insert(document).execute()
        
        if not result.data:
            console.print(f"❌ Erro ao enviar {file_path}")
            if hasattr(result, 'error'):
                console.print(f"📝 Erro: {result.error}")
            return False
            
        # Cria e envia o embedding
        doc_id = result.data[0]["id"]
        content = document["content"]
        
        console.print("🧠 Gerando embedding...")
        embedding = create_embedding(content)
        if not embedding:
            return False
            
        # Insere embedding
        embedding_data = {
            "document_id": doc_id,
            "embedding": embedding
        }
        
        embedding_result = supabase.table("embeddings").insert(embedding_data).execute()
        
        if embedding_result.data:
            console.print(f"✅ Documento {file_path} enviado com sucesso!")
            return True
            
        console.print(f"❌ Erro ao criar embedding para {file_path}")
        if hasattr(embedding_result, 'error'):
            console.print(f"📝 Erro: {embedding_result.error}")
        return False
            
    except Exception as e:
        console.print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal."""
    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return
    
    console.print("✅ Conectado ao Supabase!")
    
    # Diretório com os documentos JSON
    json_dir = Path("regras_json")
    if not json_dir.exists():
        console.print(f"❌ Diretório {json_dir} não encontrado!")
        return
    
    console.print("\nIniciando upload dos documentos para o Supabase...")
    console.print(f"Diretório: {json_dir.absolute()}\n")
    
    # Lista todos os arquivos JSON
    json_files = list(json_dir.glob("*.json"))
    console.print(f"\nEncontrados {len(json_files)} documentos para upload no Supabase.")
    
    # Processa cada documento
    start_time = time.time()
    sucessos = 0
    falhas = 0
    
    for file_path in json_files:
        if upload_document(supabase, str(file_path)):
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # Espera 1 segundo entre uploads
        console.print(f"  Processando {file_path.name}")
    
    # Estatísticas finais
    tempo_total = time.time() - start_time
    console.print(f"\nUpload para Supabase concluído em {tempo_total:.2f} segundos!")
    if sucessos > 0:
        console.print(f"✅ {sucessos} documentos enviados com sucesso")
    if falhas > 0:
        console.print(f"❌ {falhas} documentos falharam")

if __name__ == "__main__":
    main() 