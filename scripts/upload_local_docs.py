import json
import hashlib
import requests
import os
from pathlib import Path

def load_document(file_path: str) -> dict:
    """Carrega um documento JSON e adiciona um hash."""
    with open(file_path, 'r', encoding='utf-8') as f:
        doc = json.load(f)
        
    # Gera um hash do conteúdo
    content_hash = hashlib.md5(doc['content'].encode()).hexdigest()
    
    # Adiciona o hash aos metadados
    doc['metadata']['document_hash'] = content_hash
    
    return doc

def upload_document(doc: dict, api_url: str) -> dict:
    """Envia um documento para a API."""
    response = requests.post(
        f"{api_url}/documents/",
        json=doc,
        headers={'Content-Type': 'application/json'}
    )
    return response.json()

def main():
    # Configurações
    API_URL = "http://localhost:8000/api/v1"
    DOCS_DIR = Path("documents")
    
    print("🔍 Procurando documentos JSON...")
    
    # Lista todos os arquivos .json no diretório
    json_files = list(DOCS_DIR.glob("*.json"))
    print(f"📄 Encontrados {len(json_files)} documentos")
    
    # Processa cada arquivo
    for file_path in json_files:
        print(f"\n📝 Processando {file_path.name}...")
        try:
            # Carrega o documento
            doc = load_document(str(file_path))
            print(f"✅ Documento carregado: {doc['metadata'].get('title', 'Sem título')}")
            
            # Envia para a API
            print("📤 Enviando para a API...")
            result = upload_document(doc, API_URL)
            print(f"✅ Documento enviado: {result}")
            
        except Exception as e:
            print(f"❌ Erro ao processar {file_path.name}: {str(e)}")
            continue
    
    print("\n🎉 Processamento concluído!")

if __name__ == "__main__":
    main() 