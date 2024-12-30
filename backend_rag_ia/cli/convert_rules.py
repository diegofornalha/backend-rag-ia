#!/usr/bin/env python3

import json
from pathlib import Path


def create_rule_document(title, content, rule_type, source_file):
    """Cria documento JSON para uma regra."""
    return {
        "metadata_global": {
            "language": "pt-BR",
            "tipo": "regra",
            "fonte": source_file,
            "categorias": ["regras", rule_type.lower()],
        },
        "document": {
            "content": content,
            "metadata": {
                "type": rule_type,
                "title": title,
                "importancia": "alta",
                "aplicacao": "obrigatória",
                "escopo": ["desenvolvimento", "produção"],
                "formato_original": "markdown",
            },
        },
    }


def extract_content_from_md(md_content):
    """Extrai conteúdo estruturado do arquivo markdown."""
    lines = md_content.strip().split("\n")
    sections = []
    current_section = []
    current_title = ""

    for line in lines:
        if line.startswith("#"):
            if current_section:
                sections.append((current_title, "\n".join(current_section)))
                current_section = []
            current_title = line.strip("# ").strip()
        elif line.strip():
            current_section.append(line.strip())

    if current_section:
        sections.append((current_title, "\n".join(current_section)))

    return sections


def convert_md_to_json(md_file, output_dir):
    """Converte arquivo markdown em documento JSON."""
    with open(md_file, encoding="utf-8") as f:
        content = f.read()

    # Extrai o tipo da regra do nome do arquivo
    rule_type = md_file.stem.replace("REGRAS_", "").replace("_RULES", "")

    # Processa o conteúdo
    sections = extract_content_from_md(content)

    # Cria o documento principal
    main_content = "\n\n".join([f"{title}:\n{content}" for title, content in sections])
    doc = create_rule_document(
        title=md_file.stem,
        content=main_content,
        rule_type=rule_type,
        source_file=md_file.name,
    )

    # Cria nome do arquivo JSON
    json_filename = f"{md_file.stem.lower()}.json"
    output_path = output_dir / json_filename

    # Salva o documento
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    print(f"Convertido: {md_file.name} -> {output_path.name}")


def process_rules_directory(rules_dir, output_dir):
    """Processa todos os arquivos markdown no diretório de regras."""
    rules_dir = Path(rules_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for md_file in rules_dir.glob("*.md"):
        convert_md_to_json(md_file, output_dir)


if __name__ == "__main__":
    rules_dir = Path(__file__).parent.parent / "regras"
    output_dir = Path(__file__).parent.parent / "documents" / "regras"

    if not rules_dir.exists():
        print(f"Diretório de regras não encontrado: {rules_dir}")
        exit(1)

    process_rules_directory(rules_dir, output_dir)
    print("\nConversão concluída!")
