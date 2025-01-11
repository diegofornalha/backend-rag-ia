"""
Modelos para o sistema de embates.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Argumento(BaseModel):
    """Modelo para argumentos de embates."""

    nome: str
    valor: str
    tipo: str = "texto"
    descricao: str | None = None


class Embate(BaseModel):
    """Modelo para embates."""

    titulo: str
    tipo: str
    contexto: str
    status: str = "aberto"
    metadata: dict = Field(default_factory=dict)
    argumentos: list[Argumento] = Field(default_factory=list)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)
    id: str | None = None
