"""
Modelos de dados para o sistema de embates.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

class Argumento(BaseModel):
    """Modelo para argumentos em um embate."""
    autor: str = Field(..., description="Autor do argumento")
    tipo: str = Field(..., description="Tipo do argumento (técnico ou preferência)")
    conteudo: str = Field(..., description="Conteúdo do argumento")
    data: datetime = Field(default_factory=datetime.now, description="Data de criação")

class Embate(BaseModel):
    """Modelo para embates."""
    titulo: str = Field(..., description="Título do embate")
    tipo: str = Field(..., description="Tipo do embate (técnico ou preferência)")
    contexto: str = Field(..., description="Contexto que motivou o embate")
    status: str = Field(default="aberto", description="Status do embate (aberto ou resolvido)")
    data_inicio: datetime = Field(default_factory=datetime.now, description="Data de início")
    data_resolucao: Optional[datetime] = Field(None, description="Data de resolução")
    resolucao: Optional[str] = Field(None, description="Resolução do embate")
    argumentos: List[Argumento] = Field(default_factory=list, description="Lista de argumentos")
    metadata: dict = Field(default_factory=dict, description="Metadados adicionais")
    version_key: Optional[str] = Field(None, description="Chave de versionamento") 