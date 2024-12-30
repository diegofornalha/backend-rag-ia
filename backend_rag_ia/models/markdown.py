
from pydantic import BaseModel, Field


class MarkdownMetadata(BaseModel):
    """Modelo para metadados do documento markdown."""

    title: str = Field(..., description="Título do documento")
    tipo: str = Field(..., description="Tipo do documento")
    autor: str = Field(..., description="Autor do documento")
    filename: str | None = Field(None, description="Nome do arquivo original")
    categorias: list[str] | None = Field(
        default=["documentacao"], description="Categorias do documento"
    )
    tags: list[str] | None = Field(default=[], description="Tags do documento")
    versao: str | None = Field(default="1.0", description="Versão do documento")


class MarkdownUpload(BaseModel):
    """Modelo para upload de documento markdown."""

    content: str = Field(..., description="Conteúdo do documento em markdown")
    metadata: MarkdownMetadata = Field(..., description="Metadados do documento")
