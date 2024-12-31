from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SearchQuery(BaseModel):
    """Schema para validação da query de busca."""
    query: str = Field(..., min_length=3, description="Texto para busca semântica")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Limiar de similaridade")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de resultados")

class SearchResult(BaseModel):
    """Schema para resultado da busca."""
    id: str
    titulo: str
    conteudo: str
    similarity: float
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

class SearchResponse(BaseModel):
    """Schema para resposta da busca."""
    results: List[SearchResult]
    total: int
    query: str
    execution_time: float

class HealthResponse(BaseModel):
    """Schema para resposta do health check."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    uptime: float 