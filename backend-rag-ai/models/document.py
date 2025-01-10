from dataclasses import dataclass
from typing import Any


@dataclass
class Document:
    """Classe para representar um documento com seu conteúdo e metadados"""

    content: str
    metadata: dict[str, Any]
    embedding_id: int | None = None  # ID do embedding no Supabase
