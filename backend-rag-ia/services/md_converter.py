from pathlib import Path
import json
from datetime import datetime
import hashlib


class MarkdownConverter:
    @staticmethod
    def create_document(title, content, document_type, source_info):
        """Cria estrutura do documento no formato esperado pelo Supabase."""
        document_id = hashlib.md5(
            f"{title}-{datetime.now().isoformat()}".encode()
        ).hexdigest()

        return {
            "metadata_global": {
                "language": "pt-BR",
                "tipo": document_type,
                "fonte": source_info.get("filename", "upload_direto"),
                "data_criacao": datetime.now().isoformat(),
                "categorias": source_info.get("categorias", ["documentacao"]),
                "id": document_id,
            },
            "document": {
                "content": content,
                "metadata": {
                    "type": document_type,
                    "title": title,
                    "autor": source_info.get("autor", "sistema"),
                    "formato_original": "markdown",
                    "tags": source_info.get("tags", []),
                    "versao": source_info.get("versao", "1.0"),
                },
            },
        }

    @staticmethod
    def extract_content_from_md(md_content):
        """Extrai conteúdo estruturado do markdown."""
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

    @staticmethod
    def convert_md_to_json(md_content, metadata=None):
        """Converte conteúdo markdown para o formato JSON do Supabase."""
        if metadata is None:
            metadata = {}

        # Extrai seções do markdown
        sections = MarkdownConverter.extract_content_from_md(md_content)

        # Define o título como a primeira seção ou usa o fornecido
        title = metadata.get(
            "title", sections[0][0] if sections else "Documento sem título"
        )

        # Combina todas as seções em um único conteúdo
        main_content = "\n\n".join(
            [f"{title}:\n{content}" for title, content in sections]
        )

        # Cria o documento final
        document = MarkdownConverter.create_document(
            title=title,
            content=main_content,
            document_type=metadata.get("tipo", "documento"),
            source_info={
                "filename": metadata.get("filename", "upload_direto.md"),
                "autor": metadata.get("autor", "sistema"),
                "categorias": metadata.get("categorias", ["documentacao"]),
                "tags": metadata.get("tags", []),
                "versao": metadata.get("versao", "1.0"),
            },
        )

        return document

    @staticmethod
    def validate_metadata(metadata):
        """Valida e normaliza os metadados fornecidos."""
        required_fields = ["title", "tipo", "autor"]
        normalized = {}

        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Campo obrigatório ausente: {field}")

        normalized.update(metadata)

        # Garante que campos de lista existam
        normalized["categorias"] = metadata.get("categorias", ["documentacao"])
        normalized["tags"] = metadata.get("tags", [])

        return normalized
