#!/usr/bin/env python3

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from dotenv import load_dotenv
from supabase import create_client, Client
from sentence_transformers import SentenceTransformer

load_dotenv()

console = Console()
model = SentenceTransformer("all-MiniLM-L6-v2")


def check_supabase_connection() -> tuple[bool, Client]:
    """Verifica conexão com o Supabase."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            console.print(
                "❌ SUPABASE_URL e SUPABASE_KEY devem estar definidos no .env"
            )
            return False, None

        console.print("\n🔌 Conectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        return True, supabase

    except Exception as e:
        console.print(f"❌ Erro ao conectar ao Supabase: {e}")
        return False, None


def convert_document_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """Converte o formato do documento para o formato esperado pela API."""
    # Combina os metadados globais com os metadados específicos do documento
    metadata = {**data["metadata_global"], **data["document"]["metadata"]}

    # Retorna no formato esperado
    return {"content": data["document"]["content"], "metadata": metadata}


def create_embedding(content: str) -> list[float]:
    """Cria embedding para o conteúdo usando o modelo."""
    try:
        embedding = model.encode(content)
        return embedding.tolist()
    except Exception as e:
        console.print(f"❌ Erro ao criar embedding: {e}")
        return []


def calculate_document_hash(content: str, metadata: Dict[str, Any]) -> str:
    """Calcula o hash do documento baseado no conteúdo e metadados essenciais."""
    # Seleciona apenas os metadados essenciais que identificam unicamente o documento
    essential_metadata = {
        "title": metadata.get("title", ""),
        "fonte": metadata.get("fonte", ""),
        "id": metadata.get("id", ""),
        "versao": metadata.get("versao", ""),
    }

    # Cria uma string ordenada e normalizada
    doc_str = json.dumps(
        {
            "content": content.strip(),  # Remove espaços extras
            "metadata": essential_metadata,
        },
        sort_keys=True,
        ensure_ascii=False,
    )  # Preserva caracteres UTF-8

    return hashlib.sha256(doc_str.encode("utf-8")).hexdigest()


def check_document_exists(supabase: Client, doc_hash: str) -> bool:
    """Verifica se o documento já existe no Supabase."""
    try:
        response = (
            supabase.table("documents")
            .select("id")
            .eq("document_hash", doc_hash)
            .execute()
        )
        return len(response.data) > 0
    except Exception as e:
        console.print(f"❌ Erro ao verificar documento: {e}")
        return False


def upload_document(supabase: Client, file_path: str) -> tuple[bool, str]:
    """Faz upload de um documento para o Supabase. Retorna (sucesso, status)."""
    try:
        # Carrega o documento
        with open(file_path, "r") as f:
            data = json.load(f)

        # Converte para o formato esperado
        document = convert_document_format(data)

        # Calcula o hash do documento
        doc_hash = calculate_document_hash(document["content"], document["metadata"])

        # Verifica se o documento já existe
        if check_document_exists(supabase, doc_hash):
            console.print(f"⏭️ Documento {file_path} já existe, pulando...")
            return True, "pulado"

        # Adiciona o hash ao documento
        document["document_hash"] = doc_hash

        # Envia para o Supabase
        console.print(f"📤 Enviando {file_path}...")
        result = supabase.table("documents").insert(document).execute()

        if not result.data:
            console.print(f"❌ Erro ao enviar {file_path}")
            if hasattr(result, "error"):
                console.print(f"📝 Erro: {result.error}")
            return False, "erro"

        # Cria e envia o embedding
        doc_id = result.data[0]["id"]
        content = document["content"]

        console.print("🧠 Gerando embedding...")
        embedding = create_embedding(content)
        if not embedding:
            return False, "erro"

        # Insere embedding
        embedding_data = {"document_id": doc_id, "embedding": embedding}

        embedding_result = supabase.table("embeddings").insert(embedding_data).execute()

        if embedding_result.data:
            # Vincula o embedding_id ao documento
            embedding_id = embedding_result.data[0]["id"]
            update_result = (
                supabase.table("documents")
                .update({"embedding_id": embedding_id})
                .eq("id", doc_id)
                .execute()
            )

            if update_result.data:
                console.print(f"✅ Documento {file_path} enviado com sucesso!")
                return True, "sucesso"
            else:
                console.print(f"⚠️ Documento enviado mas falha ao vincular embedding_id")
                return True, "sucesso_parcial"

        console.print(f"❌ Erro ao criar embedding para {file_path}")
        if hasattr(embedding_result, "error"):
            console.print(f"📝 Erro: {embedding_result.error}")
        return False, "erro"

    except Exception as e:
        console.print(f"❌ Erro ao processar {file_path}: {e}")
        return False, "erro"


def remove_duplicates(supabase: Client) -> None:
    """Remove documentos duplicados do Supabase baseado no título."""
    try:
        console.print("\n🧹 Removendo documentos duplicados...")

        # Busca todos os documentos
        response = supabase.table("documents").select("id,metadata->title").execute()
        if not response.data:
            return

        # Agrupa por título
        docs_by_title = {}
        for doc in response.data:
            title = doc.get("title", "")
            if title in docs_by_title:
                docs_by_title[title].append(doc["id"])
            else:
                docs_by_title[title] = [doc["id"]]

        # Remove duplicatas (mantém apenas o mais recente)
        for title, ids in docs_by_title.items():
            if len(ids) > 1:
                # Ordena IDs em ordem crescente e remove todos exceto o último
                ids.sort()
                ids_to_delete = ids[:-1]  # Mantém o último (mais recente)
                console.print(
                    f"  Removendo {len(ids_to_delete)} duplicatas de '{title}'"
                )

                # Remove documentos duplicados
                supabase.table("documents").delete().in_("id", ids_to_delete).execute()

        console.print("✅ Limpeza concluída!")

    except Exception as e:
        console.print(f"❌ Erro ao remover duplicatas: {e}")


def main():
    """Função principal."""
    # Verifica conexão com Supabase
    success, supabase = check_supabase_connection()
    if not success:
        return

    console.print("✅ Conectado ao Supabase!")

    # Remove documentos duplicados
    remove_duplicates(supabase)

    # Diretório com os documentos JSON
    json_dir = Path(__file__).parent.parent / "regras_json"
    if not json_dir.exists():
        console.print(f"❌ Diretório {json_dir} não encontrado!")
        return

    console.print("\nIniciando upload dos documentos para o Supabase...")
    console.print(f"Diretório: {json_dir.absolute()}\n")

    # Lista todos os arquivos JSON
    json_files = list(json_dir.glob("*.json"))
    console.print(
        f"\nEncontrados {len(json_files)} documentos para upload no Supabase."
    )

    # Processa cada documento
    start_time = time.time()
    sucessos = 0
    falhas = 0
    pulados = 0
    sucessos_parciais = 0

    for file_path in json_files:
        success, status = upload_document(supabase, str(file_path))
        if status == "sucesso":
            sucessos += 1
        elif status == "pulado":
            pulados += 1
        elif status == "sucesso_parcial":
            sucessos_parciais += 1
        else:
            falhas += 1
        time.sleep(1)  # Espera 1 segundo entre uploads
        console.print(f"  Processando {file_path.name}")

    # Estatísticas finais
    tempo_total = time.time() - start_time
    console.print(f"\nUpload para Supabase concluído em {tempo_total:.2f} segundos!")
    if sucessos > 0:
        console.print(f"✅ {sucessos} documentos enviados com sucesso")
    if sucessos_parciais > 0:
        console.print(f"⚠️ {sucessos_parciais} documentos enviados com sucesso parcial")
    if pulados > 0:
        console.print(f"⏭️ {pulados} documentos já existiam")
    if falhas > 0:
        console.print(f"❌ {falhas} documentos falharam")


if __name__ == "__main__":
    main()
