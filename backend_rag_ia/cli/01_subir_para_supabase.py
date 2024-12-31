#!/usr/bin/env python3

import os
import hashlib
import json
from datetime import datetime
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

# Configuração do cliente Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Modelo para gerar embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(content: str):
    return model.encode(content).tolist()

def process_markdown_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read().strip()
        if not content:
            print(f"Aviso: Arquivo vazio: {file_path}")
            return None
        
        # Estrutura o conteúdo como JSONB
        content_obj = {
            "text": content,
            "format": "markdown",
            "version": "1.0",
            "encoding": "utf-8",
            "last_modified": datetime.now().isoformat(),
            "file_path": file_path
        }
        
        # Gera hash do conteúdo original
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return content_obj, content_hash

def upload_document(file_path: str, content_obj: dict, content_hash: str):
    try:
        # Verifica se documento já existe
        existing = supabase.table("01_base_conhecimento_regras_geral") \
            .select("id") \
            .eq("content_hash", content_hash) \
            .execute()
        
        if existing.data:
            print(f"Documento já existe com hash {content_hash}")
            return existing.data[0]['id']
        
        # Converte o conteúdo para JSON string
        content_json = json.dumps(content_obj)
        
        # Insere novo documento
        result = supabase.table("01_base_conhecimento_regras_geral") \
            .insert({
                "titulo": os.path.basename(file_path),
                "conteudo": content_json,
                "metadata": {"file_path": file_path}
            }) \
            .execute()
        
        if result.data:
            doc_id = result.data[0]['id']
            print(f"Documento inserido com ID: {doc_id}")
            
            # Gera e insere embedding
            embedding = create_embedding(content_obj['text'])
            
            emb_result = supabase.table("02_embeddings_regras_geral") \
                .insert({
                    "documento_id": doc_id,
                    "embedding": embedding
                }) \
                .execute()
                
            if emb_result.data:
                print(f"Embedding criado para documento {doc_id}")
            
            return doc_id
            
    except Exception as e:
        print(f"Erro ao enviar documento {file_path}: {str(e)}")
        return None

def main():
    # Diretório base dos arquivos markdown
    base_dir = "backend_rag_ia/regras_md"
    
    # Lista para armazenar documentos com falha
    falhas = []
    
    print("Iniciando processo de upload...")
    print(f"Conectado ao Supabase: {url}")
    
    # Processa todos os arquivos .md recursivamente
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(f"\nProcessando: {file_path}")
                
                result = process_markdown_file(file_path)
                if result:
                    content_obj, content_hash = result
                    if not upload_document(file_path, content_obj, content_hash):
                        falhas.append(file_path)
                else:
                    falhas.append(file_path)
    
    # Exibe resumo
    print("\nResumo do processo:")
    print(f"Total de falhas: {len(falhas)}")
    if falhas:
        print("\nArquivos com falha:")
        for f in falhas:
            print(f"- {f}")

if __name__ == "__main__":
    main()
