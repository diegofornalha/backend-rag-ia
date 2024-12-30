#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from sentence_transformers import SentenceTransformer
from supabase.client import create_client

# Adiciona o diretório raiz ao PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.md_converter import MarkdownConverter

console = Console()
load_dotenv()


def find_existing_document(supabase, filename):
    """Procura documento existente pelo nome do arquivo."""
    try:
        response = (
            supabase.table("documents")
            .select("id, content, embedding_id")
            .eq("metadata->>filename", filename)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        console.print(f"❌ Erro ao buscar documento existente: {e}")
        return None


def update_document_and_embedding(supabase, document_id, content, metadata, model):
    """Atualiza documento e embedding existentes."""
    try:
        # Atualiza o documento
        doc_result = supabase.table("documents").update({
            "content": content,
            "metadata": metadata
        }).eq("id", document_id).execute()

        if not doc_result.data:
            return False

        # Gera novo embedding
        embedding = model.encode(content)
        embedding_list = embedding.tolist()

        # Atualiza embedding existente ou cria novo
        existing_doc = doc_result.data[0]
        if existing_doc.get("embedding_id"):
            emb_result = supabase.table("embeddings").update({
                "embedding": embedding_list
            }).eq("id", existing_doc["embedding_id"]).execute()
        else:
            emb_result = supabase.table("embeddings").insert({
                "document_id": document_id,
                "embedding": embedding_list
            }).execute()

            if emb_result.data:
                # Atualiza o documento com o novo embedding_id
                embedding_id = emb_result.data[0]["id"]
                supabase.table("documents").update({
                    "embedding_id": embedding_id
                }).eq("id", document_id).execute()

        return True
    except Exception as e:
        console.print(f"❌ Erro ao atualizar documento e embedding: {e}")
        return False


def process_markdown_to_embeddings():
    """Processa arquivos markdown: converte para JSON e cria embeddings."""
    try:
        # Inicializa conexões e modelos
        console.print("🔌 Conectando ao Supabase...")
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        console.print("🧠 Carregando modelo de embeddings...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        converter = MarkdownConverter()

        # Diretórios
        md_dir = project_root / "regras_md"
        json_dir = project_root / "regras_json"

        # Verifica diretório markdown
        if not md_dir.exists():
            console.print(f"❌ Diretório {md_dir} não encontrado!")
            return

        # Cria diretório JSON se necessário
        json_dir.mkdir(exist_ok=True)

        # Lista arquivos markdown
        md_files = list(md_dir.glob("*.md"))
        console.print(f"\n📝 Encontrados {len(md_files)} arquivos markdown.")

        # Processa cada arquivo
        for md_file in md_files:
            try:
                console.print(f"\n🔄 Processando {md_file.name}...")
                
                # 1. Conversão MD → JSON
                json_file = json_dir / f"{md_file.stem.lower()}.json"
                
                with open(md_file, encoding="utf-8") as f:
                    markdown_content = f.read()

                metadata = {
                    "title": md_file.stem,
                    "tipo": "regra",
                    "autor": "sistema",
                    "filename": md_file.name,
                    "categorias": ["regras"],
                    "tags": ["documentação", "regras"],
                    "versao": "1.0",
                }

                result = converter.convert_md_to_json(
                    md_content=markdown_content,
                    metadata=metadata,
                )

                # Salva JSON
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                console.print(f"✅ JSON criado: {json_file.name}")

                # 2. Verifica se documento já existe
                content = result["document"]["content"]
                existing_doc = find_existing_document(supabase, md_file.name)

                if existing_doc:
                    if existing_doc["content"] == content:
                        console.print("ℹ️ Documento já existe e está atualizado.")
                        continue
                    
                    console.print("📝 Documento existe, atualizando...")
                    if update_document_and_embedding(supabase, existing_doc["id"], content, metadata, model):
                        console.print("✅ Documento e embedding atualizados com sucesso!")
                    else:
                        console.print("❌ Erro ao atualizar documento e embedding")
                    continue

                # 3. Se não existe, cria novo
                console.print("📤 Inserindo novo documento no Supabase...")
                doc_result = supabase.table("documents").insert({
                    "content": content,
                    "metadata": metadata
                }).execute()

                if not doc_result.data:
                    console.print("❌ Erro ao inserir documento")
                    continue

                document_id = doc_result.data[0]["id"]

                # Gera e salva embedding
                console.print("🧠 Gerando embedding...")
                embedding = model.encode(content)
                embedding_list = embedding.tolist()

                emb_result = supabase.table("embeddings").insert({
                    "document_id": document_id,
                    "embedding": embedding_list
                }).execute()

                if emb_result.data:
                    # Atualiza o documento com o embedding_id
                    embedding_id = emb_result.data[0]["id"]
                    supabase.table("documents").update({
                        "embedding_id": embedding_id
                    }).eq("id", document_id).execute()
                    console.print("✅ Novo documento e embedding criados com sucesso!")
                else:
                    console.print("❌ Erro ao salvar embedding")

            except Exception as e:
                console.print(f"❌ Erro ao processar {md_file.name}: {e}")
                continue

        console.print("\n✨ Processamento concluído!")

    except Exception as e:
        console.print(f"❌ Erro durante o processamento: {e}")


if __name__ == "__main__":
    process_markdown_to_embeddings() 