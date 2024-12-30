"""
Modelos Pydantic para o banco de dados.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Modelo base para documentos."""

    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    document_hash: str | None = None


class DocumentCreate(DocumentBase):
    """Modelo para criação de documentos."""



class Document(DocumentBase):
    """Modelo completo de documento."""

    id: int
    embedding_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração do modelo."""

        from_attributes = True


class EmbeddingBase(BaseModel):
    """Modelo base para embeddings."""

    document_id: int
    embedding: list[float]


class EmbeddingCreate(EmbeddingBase):
    """Modelo para criação de embeddings."""



class Embedding(EmbeddingBase):
    """Modelo completo de embedding."""

    id: int
    created_at: datetime

    class Config:
        """Configuração do modelo."""

        from_attributes = True
