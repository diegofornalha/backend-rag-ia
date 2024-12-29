import json
import hashlib
import requests
import time
from pathlib import Path

# URL da API
API_URL = "http://localhost:8000/api/v1"

def calculate_hash(content: str) -> str:
    """Calcula o hash do conteúdo do documento."""
    return hashlib.sha256(content.encode()).hexdigest()

def check_document_exists(document_hash: str) -> bool:
    """Verifica se o documento já existe no banco."""
    try:
        response = requests.get(f"{API_URL}/documents/check/{document_hash}")
        if response.status_code == 200:
            return response.json()["exists"]
        return False
    except Exception as e:
        print(f"Erro ao verificar documento: {e}")
        return False

def upload_document(file_path: str) -> bool:
    """Faz upload de um documento para a API."""
    try:
        # Carrega o documento
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Extrai conteúdo e metadados
        content = data["document"]["content"]
        metadata = {
            **data["metadata_global"],
            **data["document"]["metadata"]
        }
        
        # Calcula o hash do conteúdo
        document_hash = calculate_hash(content)
        
        # Verifica se já existe
        if check_document_exists(document_hash):
            print(f"📝 Documento {file_path} já existe (hash: {document_hash})")
            return True
            
        # Prepara o payload
        payload = {
            "content": content,
            "metadata": metadata,
            "document_hash": document_hash
        }
        
        # Envia para a API
        print(f"📤 Enviando {file_path}...")
        response = requests.post(f"{API_URL}/documents/", json=payload)
        
        # Verifica se o documento foi criado com sucesso (200 ou 201)
        if response.status_code in [200, 201]:
            print(f"✅ Documento {file_path} enviado com sucesso!")
            return True
            
        print(f"❌ Erro ao enviar {file_path}: {response.status_code}")
        if response.text:
            print(f"📝 Resposta: {response.text}")
        return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal."""
    # Verifica se a API está online
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code != 200:
            print("❌ API offline!")
            return
        print("✅ API online!")
    except Exception as e:
        print(f"❌ Erro ao verificar API: {e}")
        return
    
    # Lista de documentos
    documents = [
        "documents/steve_jobs.json",
        "documents/bill_gates.json",
        "documents/elon_musk.json"
    ]
    
    # Processa cada documento
    sucessos = 0
    falhas = 0
    
    for doc in documents:
        if upload_document(doc):
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # Espera 1 segundo entre uploads
    
    print(f"\n✨ Processo finalizado!")
    print(f"✅ {sucessos} documentos enviados com sucesso")
    if falhas > 0:
        print(f"❌ {falhas} documentos falharam")

if __name__ == "__main__":
    main() 