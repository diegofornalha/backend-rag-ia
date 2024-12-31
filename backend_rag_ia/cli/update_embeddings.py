"""CLI para atualizar embeddings no Supabase."""

import os
import sys
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from supabase import Client, create_client

from backend_rag_ia.constants import ERROR_SUPABASE_CONFIG
from backend_rag_ia.exceptions import SupabaseError
from backend_rag_ia.utils.logging_config import logger

# Console para output
console = Console()


def init_supabase() -> tuple[bool, Client | None]:
    """Inicializa cliente do Supabase.

    Returns:
        Tupla com sucesso e cliente

    Raises:
        SupabaseError: Se houver erro na configuração
    """
    try:
        # Verifica configuração
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            logger.error("Configuração do Supabase incompleta")
            raise SupabaseError(ERROR_SUPABASE_CONFIG)

        # Conecta
        console.print("\n🔌 Conectando ao Supabase...")
        supabase: Client = create_client(supabase_url, supabase_key)
        return True, supabase

    except Exception as e:
        logger.exception("Erro ao conectar ao Supabase: %s", e)
        return False, None


async def fetch_documents(supabase: Client) -> list[dict[str, Any]]:
    """Busca documentos no Supabase.

    Args:
        supabase: Cliente do Supabase

    Returns:
        Lista de documentos
    """
    try:
        # Busca documentos sem embedding
        response = await supabase.table("documents").select(
            "id",
            "content",
        ).is_("embedding", "null").execute()

        return response.data

    except Exception as e:
        logger.exception("Erro ao buscar documentos: %s", e)
        return []


async def update_embeddings(
    supabase: Client,
    documents: list[dict[str, Any]],
) -> tuple[int, int]:
    """Atualiza embeddings dos documentos.

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
        task = progress.add_task("Atualizando...", total=len(documents))

        # Processa cada documento
        for doc in documents:
            try:
                # Gera embedding
                content = doc["content"]
                embedding = await supabase.rpc(
                    "generate_embedding",
                    {"text": content},
                ).execute()

                # Atualiza documento
                await supabase.table("documents").update({
                    "embedding": embedding.data,
                }).eq("id", doc["id"]).execute()

                success += 1

            except Exception as e:
                logger.exception("Erro ao atualizar documento %s: %s", doc["id"], e)
                errors += 1

            progress.advance(task)

    return success, errors


def display_results(success: int, errors: int) -> None:
    """Exibe resultados da atualização.

    Args:
        success: Número de sucessos
        errors: Número de erros
    """
    # Cria tabela
    table = Table(title="\n📊 Resultados da Atualização")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right", style="green")

    # Adiciona linhas
    table.add_row("Documentos atualizados", str(success))
    table.add_row("Erros", str(errors))
    table.add_row("Total", str(success + errors))

    # Exibe tabela
    console.print(table)


async def main() -> None:
    """Função principal."""
    # Inicializa Supabase
    success, supabase = init_supabase()
    if not success:
        sys.exit(1)

    # Busca documentos
    documents = await fetch_documents(supabase)
    if not documents:
        logger.info("Nenhum documento para atualizar")
        sys.exit(0)

    # Atualiza embeddings
    success, errors = await update_embeddings(supabase, documents)
    display_results(success, errors)


if __name__ == "__main__":
    main()
