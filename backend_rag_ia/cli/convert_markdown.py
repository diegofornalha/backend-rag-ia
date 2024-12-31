"""CLI para converter arquivos markdown."""

import json
import sys
from pathlib import Path

from rich.console import Console

from backend_rag_ia.services.md_converter import MarkdownConverter
from backend_rag_ia.utils.logging_config import logger

# Console para output
console = Console()


def convert_markdown(
    input_path: Path,
    output_path: Path,
    source_info: dict[str, str],
) -> bool:
    """Converte arquivo markdown para JSON.

    Args:
        input_path: Caminho do arquivo markdown
        output_path: Caminho para salvar JSON
        source_info: Informações sobre a fonte

    Returns:
        True se convertido com sucesso
    """
    try:
        # Lê arquivo markdown
        with input_path.open() as f:
            content = f.read()

        # Converte para JSON
        converter = MarkdownConverter()
        document = converter.convert(content, source_info)

        # Salva JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(document, f, indent=2, ensure_ascii=False)

        logger.info("Convertido: %s -> %s", input_path.name, output_path.name)
        return True

    except Exception as e:
        logger.exception("Erro ao converter %s: %s", input_path, e)
        return False


def main() -> None:
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 3:
        logger.error("Uso: convert_markdown.py <input_dir> <output_dir>")
        sys.exit(1)

    # Obtém caminhos
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not input_dir.exists():
        logger.error("Diretório de entrada não encontrado: %s", input_dir)
        sys.exit(1)

    # Processa arquivos
    success = 0
    errors = 0

    for file in input_dir.glob("**/*.md"):
        # Define caminho de saída
        rel_path = file.relative_to(input_dir)
        output_path = output_dir / rel_path.with_suffix(".json")

        # Informações da fonte
        source_info = {
            "filename": file.name,
            "path": str(rel_path),
        }

        # Converte arquivo
        if convert_markdown(file, output_path, source_info):
            success += 1
        else:
            errors += 1

    # Exibe resultado
    logger.info(
        "Conversão concluída: %d sucessos, %d erros",
        success,
        errors,
    )


if __name__ == "__main__":
    main()
