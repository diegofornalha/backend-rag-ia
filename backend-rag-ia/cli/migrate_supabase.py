"""
Script para migrar dados dos JSONs para o Supabase.
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from services.vector_store import VectorStore
from models.database import Document

load_dotenv()


async def load_json_documents(directory: str = "documents") -> List[Dict[str, Any]]:
    """
    Carrega documentos dos arquivos JSON.

    Args:
        directory: Diretório com os arquivos JSON.

    Returns:
        List[Dict[str, Any]]: Lista de documentos.
    """
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            with open(os.path.join(directory, filename), "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    documents.extend(data)
                else:
                    documents.append(data)
    return documents


async def migrate_documents():
    """Migra documentos dos JSONs para o Supabase."""
    try:
        print("Iniciando migração para o Supabase...")

        # Carrega documentos
        documents = await load_json_documents()
        print(f"Carregados {len(documents)} documentos dos JSONs")

        # Inicializa VectorStore
        vector_store = VectorStore()

        # Migra cada documento
        for i, doc in enumerate(documents, 1):
            content = doc.get("content", "")
            metadata = {k: v for k, v in doc.items() if k != "content"}

            result = await vector_store.add_document(content, metadata)
            if result:
                print(f"Migrado documento {i}/{len(documents)}")
            else:
                print(f"Erro ao migrar documento {i}/{len(documents)}")

        print("Migração concluída!")

    except Exception as e:
        print(f"Erro durante a migração: {e}")


if __name__ == "__main__":
    asyncio.run(migrate_documents())
