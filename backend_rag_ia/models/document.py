"""Módulo para definição de documentos.

Este módulo fornece a classe Document para representar documentos
com seu conteúdo e metadados associados.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Document:
    """Classe para representar um documento com seu conteúdo e metadados.

    Attributes
    ----------
    content : str
        Conteúdo do documento.
    metadata : dict[str, Any]
        Metadados associados ao documento.
    embedding_id : int | None
        ID do embedding no Supabase.

    """

    content: str
    metadata: dict[str, Any]
    embedding_id: int | None = None  # ID do embedding no Supabase
