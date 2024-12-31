"""CLI para busca semântica."""

import os
import sys
from typing import Any

from rich.console import Console
from rich.table import Table
from supabase import Client, create_client

from backend_rag_ia.constants import (
    ERROR_SUPABASE_CONFIG,
    PREVIEW_LENGTH_MEDIUM,
)
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


async def search_documents(
    supabase: Client,
    query: str,
    limit: int = 5,
    threshold: float = 0.5,
) -> list[dict[str, Any]]:
    """Busca documentos por similaridade.

    Args:
        supabase: Cliente do Supabase
        query: Texto para buscar
        limit: Número máximo de resultados
        threshold: Limiar de similaridade

    Returns:
        Lista de documentos similares
    """
    try:
        # Gera embedding
        embedding = await supabase.rpc(
            "generate_embedding",
            {"text": query},
        ).execute()

        # Busca documentos
        response = await supabase.rpc(
            "match_documents",
            {
                "query_embedding": embedding.data,
                "match_count": limit,
                "similarity_threshold": threshold,
            },
        ).execute()

        return response.data

    except Exception as e:
        logger.exception("Erro na busca: %s", e)
        return []


def display_results(results: list[dict[str, Any]]) -> None:
    """Exibe resultados da busca.

    Args:
        results: Lista de documentos
    """
    if not results:
        console.print("\n❌ Nenhum resultado encontrado")
        return

    # Cria tabela
    table = Table(title="\n🔍 Resultados da busca")
    table.add_column("ID", style="cyan")
    table.add_column("Conteúdo", style="green")
    table.add_column("Similaridade", justify="right", style="magenta")

    # Adiciona resultados
    for doc in results:
        # Limita tamanho do conteúdo
        content = doc["content"]
        if len(content) > PREVIEW_LENGTH_MEDIUM:
            content = content[:PREVIEW_LENGTH_MEDIUM] + "..."

        # Adiciona linha
        doc_id = doc.get("id", "")
        similarity = f"{doc.get('similarity', 0):.2%}"
        table.add_row(doc_id, content, similarity)

    # Exibe tabela
    console.print(table)


async def main() -> None:
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 2:
        logger.error("Por favor, forneça uma query para busca!")
        return

    # Inicializa Supabase
    success, supabase = init_supabase()
    if not success:
        return

    # Realiza busca
    query = " ".join(sys.argv[1:])
    console.print(f"\n🔍 Buscando: {query}")

    results = await search_documents(supabase, query)
    display_results(results)


if __name__ == "__main__":
    main()
