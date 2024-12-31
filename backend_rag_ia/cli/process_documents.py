"""CLI para processar documentos."""

import json
import sys
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from backend_rag_ia.services.document_processor import DocumentProcessor
from backend_rag_ia.utils.logging_config import logger

# Console para output
console = Console()


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


def process_documents(
    documents: list[dict[str, Any]],
    output_dir: Path,
) -> tuple[int, int]:
    """Processa documentos.

    Args:
        documents: Lista de documentos
        output_dir: Diretório para salvar resultados

    Returns:
        Tupla com número de sucessos e erros
    """
    success = 0
    errors = 0

    # Cria diretório de saída
    output_dir.mkdir(parents=True, exist_ok=True)

    # Barra de progresso
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Processando...", total=len(documents))

        # Processa cada documento
        processor = DocumentProcessor()

        for doc in documents:
            try:
                # Processa documento
                result = processor.process(doc)

                # Salva resultado
                output_path = output_dir / f"{doc['id']}.json"
                with output_path.open("w") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                success += 1

            except Exception as e:
                logger.exception("Erro ao processar documento: %s", e)
                errors += 1

            progress.advance(task)

    return success, errors


def display_results(success: int, errors: int) -> None:
    """Exibe resultados do processamento.

    Args:
        success: Número de sucessos
        errors: Número de erros
    """
    # Cria tabela
    table = Table(title="\n📊 Resultados do Processamento")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right", style="green")

    # Adiciona linhas
    table.add_row("Documentos processados", str(success))
    table.add_row("Erros", str(errors))
    table.add_row("Total", str(success + errors))

    # Exibe tabela
    console.print(table)


def main() -> None:
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 3:
        logger.error("Uso: process_documents.py <docs_dir> <output_dir>")
        sys.exit(1)

    # Obtém caminhos
    docs_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not docs_dir.exists():
        logger.error("Diretório não encontrado: %s", docs_dir)
        sys.exit(1)

    # Carrega documentos
    documents = load_documents(docs_dir)
    if not documents:
        logger.error("Nenhum documento encontrado")
        sys.exit(1)

    # Processa documentos
    success, errors = process_documents(documents, output_dir)
    display_results(success, errors)


if __name__ == "__main__":
    main()
