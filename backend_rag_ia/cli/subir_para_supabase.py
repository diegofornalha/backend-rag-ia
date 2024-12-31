#!/usr/bin/env python3

import os
import hashlib
import json
import time
from typing import Dict, Any
import requests
from pathlib import Path

# Configuração da API
API_BASE_URL = "https://api.coflow.com.br/api/v1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def calculate_hash(content: str) -> str:
    """Calcula o hash SHA-256 do conteúdo."""
    return hashlib.sha256(content.encode()).hexdigest()

def check_document_exists(content_hash: str) -> bool:
    """Verifica se o documento já existe no Supabase usando a API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/documents/check/{content_hash}",
            headers=HEADERS
        )
        return response.status_code == 200 and response.json().get("exists", False)
    except Exception as e:
        print(f"❌ Erro ao verificar documento: {e}")
        return False

def process_markdown(file_path: str, base_dir: str) -> Dict[str, Any]:
    """Processa arquivo markdown e extrai conteúdo e metadados."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Calcula o caminho relativo corretamente
        abs_file_path = Path(file_path).resolve()
        abs_base_dir = Path(base_dir).resolve()
        rel_path = abs_file_path.relative_to(abs_base_dir)

        # Extrai metadados básicos do arquivo
        metadata = {
            "filename": os.path.basename(file_path),
            "path": str(rel_path),
            "type": "markdown",
            "public": True,
            "category": rel_path.parent.name,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return {
            "content": content,
            "metadata": metadata,
            "content_hash": calculate_hash(content)
        }
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return None

def upload_document(document: Dict[str, Any]) -> bool:
    """Faz upload do documento para o Supabase via API."""
    try:
        if check_document_exists(document["content_hash"]):
            print(f"📝 Documento já existe (hash: {document['content_hash']})")
            return True

        payload = {
            "titulo": document["metadata"]["filename"],
            "conteudo": document["content"],
            "metadata": document["metadata"],
            "content_hash": document["content_hash"]
        }

        response = requests.post(
            f"{API_BASE_URL}/documents",
            headers=HEADERS,
            json=payload
        )

        if response.status_code in [200, 201]:
            print(f"✅ Documento enviado com sucesso!")
            return True

        print(f"❌ Erro ao enviar documento: {response.status_code}")
        print(f"📝 Resposta: {response.text}")
        return False

    except Exception as e:
        print(f"❌ Erro no upload: {e}")
        return False

def upload_directory(directory: str) -> tuple[int, int]:
    """Faz upload de todos os arquivos markdown de um diretório."""
    sucessos = 0
    falhas = 0
    base_dir = os.path.dirname(os.path.dirname(directory))

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                print(f"\n📤 Processando {file_path}...")
                
                document = process_markdown(file_path, base_dir)
                if document and upload_document(document):
                    sucessos += 1
                else:
                    falhas += 1
                
                time.sleep(1)  # Evita sobrecarga da API

    return sucessos, falhas

def main():
    """Função principal."""
    print("🚀 Iniciando upload para Supabase via API Render...")

    # Verifica se a API está online
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ API offline!")
            return
        print("✅ API online!")
    except Exception as e:
        print(f"❌ Erro ao verificar API: {e}")
        return

    # Diretório com os arquivos markdown
    directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "regras_md")
    
    if not os.path.exists(directory):
        print(f"❌ Diretório {directory} não encontrado!")
        return

    print(f"\n📁 Processando diretório: {directory}")
    sucessos, falhas = upload_directory(directory)

    print("\n✨ Processo finalizado!")
    print(f"✅ {sucessos} documentos enviados com sucesso")
    if falhas > 0:
        print(f"❌ {falhas} documentos falharam")

if __name__ == "__main__":
    main()
