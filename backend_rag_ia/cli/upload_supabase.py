#!/usr/bin/env python3

import os
from pathlib import Path

from dotenv import load_dotenv
from markdown_converter import MarkdownConverter
from rich.console import Console
from sentence_transformers import SentenceTransformer
from supabase import create_client

load_dotenv()

console = Console()
project_root = Path(__file__).parent.parent.parent

def find_existing_document(supabase, filename):
    """Verifica se o documento já existe no Supabase."""
    try:
        response = (
            supabase.table("documents")
            .select("id")
            .eq("filename", filename)
            .execute()
        )
        return response.data[0] if response.data else None
    except Exception as e:
        console.print(f"❌ Erro ao verificar documento: {e}")
        return None

def handle_existing_document(existing_doc, content, metadata, supabase, model):
    """Atualiza um documento existente."""
    try:
        doc_id = existing_doc["id"]
        document = {"content": content, "metadata": metadata}
        # Atualiza documento
        supabase.table("documents").update(document).eq("id", doc_id).execute()
        # Atualiza embedding
        embedding = model.encode(content).tolist()
        supabase.table("embeddings").update({"embedding": embedding}).eq("document_id", doc_id).execute()
        console.print("✅ Documento atualizado com sucesso!")
    except Exception as e:
        console.print(f"❌ Erro ao atualizar documento: {e}")

def create_new_document(content, metadata, supabase, model):
    """Cria um novo documento."""
    try:
        # Cria documento
        document = {"content": content, "metadata": metadata}
        result = supabase.table("documents").insert(document).execute()
        if not result.data:
            console.print("❌ Erro ao criar documento")
            return
        # Cria embedding
        doc_id = result.data[0]["id"]
        embedding = model.encode(content).tolist()
        embedding_data = {"document_id": doc_id, "embedding": embedding}
        supabase.table("embeddings").insert(embedding_data).execute()
        console.print("✅ Documento criado com sucesso!")
    except Exception as e:
        console.print(f"❌ Erro ao criar documento: {e}")

def init_services():
    """Inicializa serviços necessários."""
    console.print("🔌 Conectando ao Supabase...")
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    console.print("🧠 Carregando modelo de embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    converter = MarkdownConverter()
    return supabase, model, converter

def setup_directories():
    """Configura diretórios de trabalho."""
    md_dir = project_root / "regras_md"
    json_dir = project_root / "regras_json"
    if not md_dir.exists():
        console.print(f"❌ Diretório {md_dir} não encontrado!")
        return None, None
    json_dir.mkdir(exist_ok=True)
    return md_dir, json_dir

def process_single_file(md_file, converter, supabase, model):
    """Processa um único arquivo markdown."""
    console.print(f"\n🔄 Processando {md_file.name}...")
    # Conversão MD → JSON
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
    # Verifica documento existente
    content = result["document"]["content"]
    existing_doc = find_existing_document(supabase, md_file.name)
    if existing_doc:
        handle_existing_document(existing_doc, content, metadata, supabase, model)
    else:
        create_new_document(content, metadata, supabase, model)

def main():
    """Função principal."""
    try:
        # Inicializa serviços
        supabase, model, converter = init_services()
        # Configura diretórios
        md_dir, json_dir = setup_directories()
        if not md_dir or not json_dir:
            return
        # Lista arquivos markdown
        md_files = list(md_dir.glob("*.md"))
        console.print(f"\n📝 Encontrados {len(md_files)} arquivos markdown.")
        # Processa cada arquivo
        for md_file in md_files:
            try:
                process_single_file(md_file, converter, supabase, model)
            except Exception as e:
                console.print(f"❌ Erro ao processar {md_file.name}: {e}")
                continue
        console.print("\n✨ Processamento concluído!")
    except Exception as e:
        console.print(f"❌ Erro durante o processamento: {e}")

if __name__ == "__main__":
    main()
