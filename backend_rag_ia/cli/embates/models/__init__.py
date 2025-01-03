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
    descricao: Optional[str] = None

class Embate(BaseModel):
    """Modelo para embates."""
    titulo: str
    tipo: str
    contexto: str
    status: str = "aberto"
    metadata: Dict = Field(default_factory=dict)
    argumentos: List[Argumento] = Field(default_factory=list)
    criado_em: datetime = Field(default_factory=datetime.now)
    atualizado_em: datetime = Field(default_factory=datetime.now)
    id: Optional[str] = None
