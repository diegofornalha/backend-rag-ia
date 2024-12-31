#!/usr/bin/env python3

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from sentence_transformers import SentenceTransformer
from supabase.client import create_client

load_dotenv()
console = Console()

def upload_embeddings():
    """Upload de embeddings para o Supabase."""
    try:
        # Conexão com Supabase
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

        # Carrega o modelo
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Diretório com os arquivos JSON
        json_dir = Path(__file__).parent.parent / "regras_json"
        if not json_dir.exists():
            console.print(f"❌ Diretório {json_dir} não encontrado!")
            return

        # Processa cada arquivo
        for file_path in json_dir.glob("*.json"):
            console.print(f"\n📄 Processando {file_path.name}")

            # Lê o conteúdo do arquivo
            with open(file_path) as f:
                data = json.load(f)
                content = data["document"]["content"]

            # Primeiro, insere o documento
            console.print("📝 Inserindo documento...")
            doc_result = supabase.table("documents").insert({
                "content": content,
                "metadata": data["document"]["metadata"]
            }).execute()

            if not doc_result.data:
                console.print("❌ Erro ao inserir documento")
                continue

            document_id = doc_result.data[0]["id"]

            # Gera o embedding
            console.print("🧠 Gerando embedding...")
            embedding = model.encode(content)

            # Converte para lista Python
            embedding_list = embedding.tolist()

            # Salva o embedding
            result = supabase.table("embeddings").insert({
                "document_id": document_id,
                "embedding": embedding_list
            }).execute()

            if result.data:
                console.print("✅ Embedding salvo com sucesso!")
            else:
                console.print("❌ Erro ao salvar embedding")

    except Exception as e:
        console.print(f"❌ Erro: {e}")

if __name__ == "__main__":
    upload_embeddings()
