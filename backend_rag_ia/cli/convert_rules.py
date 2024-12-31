"""CLI para converter regras markdown para JSON."""

import json
import sys
from pathlib import Path

from rich.console import Console

from backend_rag_ia.services.md_converter import MarkdownConverter
from backend_rag_ia.utils.logging_config import logger

# Console para output
console = Console()


def convert_rule(
    md_file: Path,
    output_path: Path,
    source_info: dict[str, str],
) -> bool:
    """Converte arquivo de regra para JSON.

    Args:
        md_file: Caminho do arquivo markdown
        output_path: Caminho para salvar JSON
        source_info: Informações sobre a fonte

    Returns:
        True se convertido com sucesso
    """
    try:
        # Lê arquivo markdown
        with md_file.open() as f:
            content = f.read()

        # Converte para JSON
        converter = MarkdownConverter()
        document = converter.convert(
            content,
            {
                **source_info,
                "tipo": "regra",
                "categorias": ["regras"],
                "tags": ["documentação", "regras"],
                "versao": "1.0",
            },
        )

        # Salva JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(document, f, ensure_ascii=False, indent=2)

        logger.info("Convertido: %s -> %s", md_file.name, output_path.name)
        return True

    except Exception as e:
        logger.exception("Erro ao converter %s: %s", md_file, e)
        return False


def process_rules_directory(rules_dir: Path, output_dir: Path) -> None:
    """Processa diretório de regras.

    Args:
        rules_dir: Diretório com arquivos markdown
        output_dir: Diretório para salvar JSONs
    """
    # Lista arquivos markdown
    md_files = list(rules_dir.glob("**/*.md"))
    logger.info("Encontrados %d arquivos markdown", len(md_files))

    # Processa cada arquivo
    success = 0
    errors = 0

    for md_file in md_files:
        # Define caminho de saída
        rel_path = md_file.relative_to(rules_dir)
        output_path = output_dir / rel_path.with_suffix(".json")

        # Informações da fonte
        source_info = {
            "filename": md_file.name,
            "path": str(rel_path),
        }

        # Converte arquivo
        if convert_rule(md_file, output_path, source_info):
            success += 1
        else:
            errors += 1

    # Exibe resultado
    logger.info(
        "Conversão concluída: %d sucessos, %d erros",
        success,
        errors,
    )


def main() -> None:
    """Função principal."""
    # Verifica argumentos
    if len(sys.argv) < 3:
        logger.error("Uso: convert_rules.py <rules_dir> <output_dir>")
        sys.exit(1)

    # Obtém caminhos
    rules_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not rules_dir.exists():
        logger.error("Diretório de regras não encontrado: %s", rules_dir)
        sys.exit(1)

    # Processa diretório
    process_rules_directory(rules_dir, output_dir)


if __name__ == "__main__":
    main()
