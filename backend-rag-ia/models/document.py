from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Document:
    """Classe para representar um documento com seu conteúdo e metadados"""

    content: str
    metadata: Dict[str, Any]
    embedding_id: Optional[int] = None  # ID no índice FAISS
