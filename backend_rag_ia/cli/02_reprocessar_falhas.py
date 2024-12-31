#!/usr/bin/env python3

import os
import hashlib
import time
import base64
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from rich.console import Console
from sentence_transformers import SentenceTransformer

# Carrega variáveis de ambiente
load_dotenv()
console = Console()
model = SentenceTransformer("all-MiniLM-L6-v2")

# Lista de arquivos que falharam
ARQUIVOS_FALHA = [
    "regras_md/3_deployment/d_regras_docker.md",
    "regras_md/2_database/a_regras_sql.md",
    "regras_md/2_database/f_problemas_docker.md",
    "regras_md/1_core/f_regras_verificacao_dupla.md",
    "regras_md/1_core/b_project_rules.md",
    "regras_md/1_core/d_regras_documentacao.md"
]

def normalize_content(content: str) -> str:
    """Normaliza o conteúdo do arquivo."""
    # Remove BOM se presente
    content = content.replace('\ufeff', '')
    # Normaliza quebras de linha para LF
    content = content.replace('\r\n', '\n')
    # Remove caracteres de controle exceto newline
    content = ''.join(char for char in content if char == '\n' or char.isprintable())
    return content

def process_markdown(file_path: str) -> Dict[str, Any]:
    """Processa arquivo markdown com verificações adicionais."""
    try:
        # Lê o arquivo garantindo UTF-8
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            console.print(f"⚠️ Arquivo vazio: {file_path}")
            return None

        # Normaliza o conteúdo
        content = normalize_content(content)

        # Codifica o conteúdo em base64
        content_bytes = content.encode('utf-8')
        content_base64 = base64.b64encode(content_bytes).decode('utf-8')

        # Extrai metadados básicos
        metadata = {
            "filename": os.path.basename(file_path),
            "path": file_path,
            "type": "markdown",
            "public": True,
            "category": Path(file_path).parent.name,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Calcula o hash do conteúdo normalizado
        content_hash = hashlib.sha256(content_bytes).hexdigest()

        return {
            "titulo": metadata["filename"],
            "conteudo": content_base64,  # Conteúdo em base64
            "metadata": metadata,
            "content_hash": content_hash,
            "raw_content": content  # Mantém o conteúdo original para embeddings
        }
    except Exception as e:
        console.print(f"❌ Erro ao processar {file_path}: {e}")
        return None

def sync_embedding(supabase: Client, doc_id: str, content: str) -> bool:
    """Sincroniza o embedding de um documento."""
    try:
        # Verifica se já existe embedding
        response = supabase.table("02_embeddings_regras_geral") \
            .select("id") \
            .eq("documento_id", doc_id) \
            .execute()
        
        if response.data:
            console.print(f"📝 Embedding já existe para documento {doc_id}")
            return True

        # Cria embedding
        embedding = model.encode(content)
        if not isinstance(embedding, list):
            embedding = embedding.tolist()

        # Insere embedding diretamente
        data = {
            "documento_id": doc_id,
            "embedding": embedding
        }
        result = supabase.table("02_embeddings_regras_geral").insert(data).execute()

        if result.data:
            console.print("✅ Embedding sincronizado com sucesso!")
            return True

        console.print("❌ Erro ao sincronizar embedding")
        if hasattr(result, "error"):
            console.print(f"📝 Erro: {result.error}")
        return False

    except Exception as e:
        console.print(f"❌ Erro ao sincronizar embedding: {e}")
        return False

def upload_document(supabase: Client, document: Dict[str, Any]) -> bool:
    """Faz upload do documento para o Supabase."""
    try:
        # Verifica se documento já existe
        response = supabase.table("01_base_conhecimento_regras_geral") \
            .select("id") \
            .eq("content_hash", document["content_hash"]) \
            .execute()

        if response.data:
            doc_id = response.data[0]["id"]
            console.print(f"📝 Documento já existe (hash: {document['content_hash']})")
            return sync_embedding(supabase, doc_id, document["raw_content"])

        # Insere o documento
        response = supabase.table("01_base_conhecimento_regras_geral").insert({
            "titulo": document["titulo"],
            "conteudo": document["conteudo"],  # Conteúdo em base64
            "metadata": document["metadata"]
        }).execute()

        if response.data:
            doc_id = response.data[0]["id"]
            console.print(f"✅ Documento enviado com sucesso!")
            return sync_embedding(supabase, doc_id, document["raw_content"])

        console.print(f"❌ Erro ao enviar documento")
        return False

    except Exception as e:
        console.print(f"❌ Erro no upload: {e}")
        return False

def main():
    """Função principal."""
    console.print("\n🔄 Reprocessando arquivos que falharam...")

    # Inicializa cliente Supabase
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            console.print("❌ SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env")
            return
            
        supabase = create_client(url, key)
        console.print("✅ Conectado ao Supabase!")
    except Exception as e:
        console.print(f"❌ Erro ao conectar ao Supabase: {e}")
        return

    # Processa cada arquivo que falhou
    sucessos = 0
    falhas = 0
    falhas_lista = []

    for arquivo in ARQUIVOS_FALHA:
        console.print(f"\n📄 Processando: {arquivo}")
        
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), arquivo)
        if not os.path.exists(file_path):
            console.print(f"❌ Arquivo não encontrado: {file_path}")
            continue

        document = process_markdown(file_path)
        if document and upload_document(supabase, document):
            sucessos += 1
        else:
            falhas += 1
            falhas_lista.append(arquivo)

        time.sleep(0.5)  # Pequeno delay entre uploads

    # Resultados
    console.print("\n✨ Processo finalizado!")
    console.print(f"✅ {sucessos} documentos reprocessados com sucesso")
    if falhas > 0:
        console.print(f"❌ {falhas} documentos falharam novamente:")
        for arquivo in falhas_lista:
            console.print(f"  - {arquivo}")

if __name__ == "__main__":
    main() 