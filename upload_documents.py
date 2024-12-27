import json
import requests
import time
import os
import hashlib

API_URL = "https://backend-rag-ia.onrender.com/api/v1"
DOCUMENTS = [
    "documents/steve_jobs.json",
    "documents/bill_gates.json",
    "documents/elon_musk.json"
]

def generate_document_hash(content):
    """Gera um hash único para o documento baseado apenas no conteúdo."""
    # Normaliza o texto: remove espaços extras e converte para minúsculas
    normalized_content = " ".join(content.lower().split())
    # Gera o hash usando SHA-256 que é mais seguro que MD5
    return hashlib.sha256(normalized_content.encode()).hexdigest()

def format_document(data):
    """Formata o documento para o formato esperado pela API."""
    content = data["document"]["content"]
    return {
        "content": content,
        "metadata": {
            **data["document"]["metadata"],
            **data["metadata_global"],
            "document_hash": generate_document_hash(content)
        }
    }

def check_document_exists(document_hash):
    """Verifica se o documento já existe no Supabase."""
    try:
        response = requests.get(
            f"{API_URL}/documents/check/{document_hash}",
            headers={"Content-Type": "application/json"}
        )
        return response.status_code == 200
    except:
        return False

def upload_document(file_path):
    try:
        with open(file_path, 'r') as f:
            raw_document = json.load(f)
        
        # Formata o documento
        document = format_document(raw_document)
        document_hash = document["metadata"]["document_hash"]
        
        # Verifica se já existe
        if check_document_exists(document_hash):
            print(f"⚠️ Documento {file_path} já existe, pulando...")
            return
        
        print(f"\nEnviando {file_path}...")
        response = requests.post(
            f"{API_URL}/documents/",
            json=document,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print(f"✅ {file_path} enviado com sucesso!")
            print(f"Resposta: {response.json()}")
        else:
            print(f"❌ Erro ao enviar {file_path}")
            print(f"Status: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except FileNotFoundError:
        print(f"❌ Arquivo {file_path} não encontrado")
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar {file_path} - formato JSON inválido")
    except Exception as e:
        print(f"❌ Erro inesperado ao enviar {file_path}: {str(e)}")

def main():
    print("🚀 Iniciando upload dos documentos...")
    
    # Verifica se a API está online
    try:
        health = requests.get(f"{API_URL}/health")
        if health.status_code != 200:
            print("❌ API não está respondendo!")
            return
        print("✅ API está online!")
    except Exception as e:
        print(f"❌ Erro ao verificar status da API: {str(e)}")
        return
    
    # Verifica se o diretório documents existe
    if not os.path.exists("documents"):
        print("❌ Diretório 'documents' não encontrado!")
        return
    
    # Primeira leva de documentos
    print("\n📦 Enviando primeira leva de documentos...")
    for doc in DOCUMENTS[:1]:  # Apenas Steve Jobs
        upload_document(doc)
        time.sleep(2)
    
    # Segunda leva
    print("\n📦 Enviando segunda leva de documentos...")
    for doc in DOCUMENTS[1:2]:  # Apenas Bill Gates
        upload_document(doc)
        time.sleep(2)
    
    # Terceira leva
    print("\n📦 Enviando terceira leva de documentos...")
    for doc in DOCUMENTS[2:]:  # Apenas Elon Musk
        upload_document(doc)
        time.sleep(2)
    
    # Teste de duplicidade
    print("\n🔄 Testando duplicidade...")
    print("Tentando enviar Steve Jobs novamente...")
    upload_document(DOCUMENTS[0])
    
    print("\n✨ Processo finalizado!")

if __name__ == "__main__":
    main() 