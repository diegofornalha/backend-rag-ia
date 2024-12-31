"""CLI para indexar documentos no Supabase."""

import json
import os
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from supabase import Client, create_client

from backend_rag_ia.utils.logging_config import logger

# Console para output
console = Console()


def init_supabase() -> tuple[bool, Client | None]:
    """Inicializa cliente do Supabase.

    Returns:
        Tupla com sucesso e cliente
    """
    try:
        # Verifica configuração
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            console.print("❌ SUPABASE_URL e SUPABASE_KEY devem ser configurados!")
            return False, None

        # Conecta
        console.print("\n🔌 Conectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        return True, supabase

    except Exception as e:
        console.print(f"❌ Erro ao conectar ao Supabase: {e}")
        return False, None


def load_documents(docs_dir: Path) -> list[dict[str, Any]]:
    """Carrega documentos JSON.

    Args:
        docs_dir: Diretório com arquivos JSON

    Returns:
        Lista de documentos
    """
    documents = []

    # Lista arquivos JSON
    json_files = list(docs_dir.glob("**/*.json"))
    logger.info("Encontrados %d arquivos JSON", len(json_files))

    # Carrega cada arquivo
    for json_file in json_files:
        try:
            with json_file.open() as f:
                doc = json.load(f)
                documents.append(doc)

        except Exception as e:
            logger.exception("Erro ao carregar %s: %s", json_file, e)

    return documents


async def index_documents(
    supabase: Client,
    documents: list[dict[str, Any]],
) -> tuple[int, int]:
    """Indexa documentos no Supabase.

    Args:
        supabase: Cliente do Supabase
        documents: Lista de documentos

    Returns:
        Tupla com número de sucessos e erros
    """
    success = 0
    errors = 0

    # Barra de progresso
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Indexando...", total=len(documents))

        # Processa cada documento
        for doc in documents:
            try:
                # Gera embedding
                content = doc["content"]
                embedding = await supabase.rpc(
                    "generate_embedding",
                    {"text": content},
                ).execute()

                # Insere documento
                await supabase.table("documents").insert({
                    "content": content,
                    "embedding": embedding.data,
                    "metadata": doc.get("metadata", {}),
                }).execute()

                success += 1

            except Exception as e:
                logger.exception("Erro ao indexar documento: %s", e)
                errors += 1

            progress.advance(task)

    return success, errors


def display_results(success: int, errors: int) -> None:
    """Exibe resultados da indexação.

    Args:
        success: Número de sucessos
        errors: Número de erros
    """
    # Cria tabela
    table = Table(title="\n📊 Resultados da Indexação")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right", style="green")

    # Adiciona linhas
    table.add_row("Documentos indexados", str(success))
    table.add_row("Erros", str(errors))
    table.add_row("Total", str(success + errors))

    # Exibe tabela
    console.print(table)


async def main() -> None:
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 2:
        logger.error("Uso: index_documents.py <docs_dir>")
        sys.exit(1)

    # Obtém caminho
    docs_dir = Path(sys.argv[1])

    if not docs_dir.exists():
        logger.error("Diretório não encontrado: %s", docs_dir)
        sys.exit(1)

    # Inicializa Supabase
    success, supabase = init_supabase()
    if not success:
        sys.exit(1)

    # Carrega documentos
    documents = load_documents(docs_dir)
    if not documents:
        logger.error("Nenhum documento encontrado")
        sys.exit(1)

    # Indexa documentos
    success, errors = await index_documents(supabase, documents)
    display_results(success, errors)


if __name__ == "__main__":
    main()
