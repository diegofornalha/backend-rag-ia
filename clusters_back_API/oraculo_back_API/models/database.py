"""
Modelos Pydantic para o banco de dados.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    """Modelo base para documentos."""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_hash: Optional[str] = None

class DocumentCreate(DocumentBase):
    """Modelo para criação de documentos."""
    pass

class Document(DocumentBase):
    """Modelo completo de documento."""
    id: int
    embedding_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração do modelo."""
        from_attributes = True

class EmbeddingBase(BaseModel):
    """Modelo base para embeddings."""
    document_id: int
    embedding: List[float]

class EmbeddingCreate(EmbeddingBase):
    """Modelo para criação de embeddings."""
    pass

class Embedding(EmbeddingBase):
    """Modelo completo de embedding."""
    id: int
    created_at: datetime

    class Config:
        """Configuração do modelo."""
        from_attributes = True 