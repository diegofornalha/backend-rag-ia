from pydantic import BaseModel, Field
from typing import List, Optional


class MarkdownMetadata(BaseModel):
    """Modelo para metadados do documento markdown."""

    title: str = Field(..., description="Título do documento")
    tipo: str = Field(..., description="Tipo do documento")
    autor: str = Field(..., description="Autor do documento")
    filename: Optional[str] = Field(None, description="Nome do arquivo original")
    categorias: Optional[List[str]] = Field(
        default=["documentacao"], description="Categorias do documento"
    )
    tags: Optional[List[str]] = Field(default=[], description="Tags do documento")
    versao: Optional[str] = Field(default="1.0", description="Versão do documento")


class MarkdownUpload(BaseModel):
    """Modelo para upload de documento markdown."""

    content: str = Field(..., description="Conteúdo do documento em markdown")
    metadata: MarkdownMetadata = Field(..., description="Metadados do documento")
