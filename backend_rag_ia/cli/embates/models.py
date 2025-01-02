"""
Modelos de dados para embates.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Argumento(BaseModel):
    """Modelo para argumentos em embates."""
    
    autor: str
    tipo: str
    conteudo: str
    data: datetime = Field(default_factory=datetime.now)

class Embate(BaseModel):
    """Modelo para embates."""
    
    titulo: str
    tipo: str
    contexto: str
    status: str = "aberto"
    data_inicio: datetime = Field(default_factory=datetime.now)
    argumentos: List[Argumento] = []
    resolucao: Optional[str] = None
    arquivo: Optional[str] = None
    metadata: dict = Field(default_factory=dict) 