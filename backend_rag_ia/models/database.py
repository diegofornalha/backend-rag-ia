"""Módulo para modelos do banco de dados.

Este módulo fornece classes e funções para interagir com o banco de dados,
incluindo modelos para documentos e embeddings.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class Document(BaseModel):
    """Modelo para documentos no banco de dados.

    Attributes
    ----------
    id : str
        Identificador único do documento.
    titulo : str
        Título do documento.
    conteudo : str
        Conteúdo do documento.
    metadata : dict[str, Any] | None
        Metadados do documento.
    created_at : datetime
        Data de criação.
    updated_at : datetime | None
        Data da última atualização.

    """

    id: str
    titulo: str
    conteudo: str
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class Embedding(BaseModel):
    """Modelo para embeddings no banco de dados.

    Attributes
    ----------
    id : str
        Identificador único do embedding.
    document_id : str
        ID do documento associado.
    embedding : list[float]
        Vetor do embedding.
    created_at : datetime
        Data de criação.
    updated_at : datetime | None
        Data da última atualização.

    """

    id: str
    document_id: str
    embedding: list[float]
    created_at: datetime
    updated_at: Optional[datetime] = None
