"""
Modelos de dados para embates.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Argumento(BaseModel):
    """Schema para argumentos de embates."""
    autor: str
    conteudo: str
    tipo: str = Field(..., pattern="^(tecnico|preferencia)$")
    data: datetime

class Embate(BaseModel):
    """Schema para embates com validação."""
    titulo: str
    tipo: str = Field(..., pattern="^(tecnico|preferencia)$")
    contexto: str
    status: str = Field(..., pattern="^(aberto|resolvido)$")
    data_inicio: datetime
    argumentos: List[Argumento]
    decisao: Optional[str]
    razao: Optional[str]
    arquivo: str
    version_key: Optional[str]
    error_log: Optional[dict]
    metadata: Optional[dict] = Field(default_factory=dict) 