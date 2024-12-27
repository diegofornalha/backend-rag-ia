import json
import requests
import time
import os

API_URL = "https://backend-rag-ia.onrender.com/api/v1"
DOCUMENTS = [
    "documents/steve_jobs.json",
    "documents/bill_gates.json",
    "documents/elon_musk.json"
]

def format_document(data):
    """Formata o documento para o formato esperado pela API."""
    return {
        "content": data["document"]["content"],
        "metadata": {
            **data["document"]["metadata"],
            **data["metadata_global"]
        }
    }

def upload_document(file_path):
    try:
        with open(file_path, 'r') as f:
            raw_document = json.load(f)
        
        # Formata o documento
        document = format_document(raw_document)
        
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
    
    # Upload dos documentos
    for doc in DOCUMENTS:
        upload_document(doc)
        time.sleep(2)  # Espera 2 segundos entre cada upload
    
    print("\n✨ Processo finalizado!")

if __name__ == "__main__":
    main() 