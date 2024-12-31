#!/usr/bin/env python3

import os
import hashlib
import time
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Carrega variáveis de ambiente
load_dotenv()
console = Console()

def calculate_hash(content: str) -> str:
    """Calcula o hash SHA-256 do conteúdo."""
    return hashlib.sha256(content.encode()).hexdigest()

def check_document_exists(supabase: Client, content_hash: str) -> bool:
    """Verifica se o documento já existe no Supabase."""
    try:
        response = supabase.table("01_base_conhecimento_regras_geral") \
            .select("id") \
            .eq("content_hash", content_hash) \
            .execute()
        return len(response.data) > 0
    except Exception as e:
        console.print(f"❌ Erro ao verificar documento: {e}")
        return False

def process_markdown(file_path: str, base_dir: str) -> Dict[str, Any]:
    """Processa arquivo markdown e extrai conteúdo e metadados."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            console.print(f"⚠️ Arquivo vazio: {file_path}")
            return None

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

        # Calcula o hash do conteúdo
        content_hash = calculate_hash(content)

        return {
            "titulo": metadata["filename"],
            "conteudo": content,
            "metadata": metadata,
            "content_hash": content_hash
        }
    except Exception as e:
        console.print(f"❌ Erro ao processar {file_path}: {e}")
        return None

def upload_document(supabase: Client, document: Dict[str, Any]) -> bool:
    """Faz upload do documento para o Supabase."""
    try:
        if check_document_exists(supabase, document["content_hash"]):
            console.print(f"📝 Documento já existe (hash: {document['content_hash']})")
            return True

        # Insere o documento
        response = supabase.table("01_base_conhecimento_regras_geral").insert({
            "titulo": document["titulo"],
            "conteudo": document["conteudo"],  # Envia como texto simples
            "metadata": document["metadata"],
            "content_hash": document["content_hash"]  # Inclui o hash explicitamente
        }).execute()

        if response.data:
            console.print(f"✅ Documento enviado com sucesso!")
            return True

        console.print(f"❌ Erro ao enviar documento")
        console.print(f"📝 Resposta: {response}")
        return False

    except Exception as e:
        console.print(f"❌ Erro no upload: {e}")
        return False

def upload_directory(supabase: Client, directory: str) -> tuple[int, int]:
    """Faz upload de todos os arquivos markdown de um diretório."""
    sucessos = 0
    falhas = 0
    base_dir = os.path.dirname(os.path.dirname(directory))

    # Lista todos os arquivos .md recursivamente
    md_files = list(Path(directory).rglob("*.md"))
    total_files = len(md_files)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Processando arquivos...", total=total_files)

        for file_path in md_files:
            progress.update(task, description=f"📤 Processando {file_path.name}...")
            
            document = process_markdown(str(file_path), base_dir)
            if document and upload_document(supabase, document):
                sucessos += 1
            else:
                falhas += 1
            
            progress.advance(task)
            time.sleep(0.5)  # Pequeno delay para evitar sobrecarga

    return sucessos, falhas

def main():
    """Função principal."""
    console.print("\n🚀 Iniciando upload de documentos para o Supabase...")

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

    # Diretório com os arquivos markdown
    directory = os.path.join(os.path.dirname(os.path.dirname(__file__)), "regras_md")
    
    if not os.path.exists(directory):
        console.print(f"❌ Diretório {directory} não encontrado!")
        return

    console.print(f"\n📁 Processando diretório: {directory}")
    sucessos, falhas = upload_directory(supabase, directory)

    console.print("\n✨ Processo finalizado!")
    console.print(f"✅ {sucessos} documentos enviados com sucesso")
    if falhas > 0:
        console.print(f"❌ {falhas} documentos falharam")

if __name__ == "__main__":
    main()
