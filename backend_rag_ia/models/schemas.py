"""Módulo para schemas do modelo.

Este módulo fornece schemas para validação e serialização
de dados do modelo, incluindo resultados de busca.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Schema para validação da query de busca.

    Attributes
    ----------
    query : str
        Texto para busca semântica.
    threshold : float
        Limiar de similaridade.
    limit : int
        Número máximo de resultados.

    """

    query: str = Field(..., min_length=3, description="Texto para busca semântica")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Limiar de similaridade")
    limit: int = Field(10, ge=1, le=100, description="Número máximo de resultados")


class SearchResult(BaseModel):
    """Resultado de uma busca.

    Attributes
    ----------
    document_id : str
        ID do documento encontrado.
    score : float
        Pontuação de relevância.
    content : str
        Trecho relevante do conteúdo.

    """

    document_id: str
    score: float
    content: str


class SearchResponse(BaseModel):
    """Resposta de uma busca.

    Attributes
    ----------
    query : str
        Consulta realizada.
    results : list[SearchResult]
        Resultados encontrados.

    """

    query: str
    results: list[SearchResult]


class HealthResponse(BaseModel):
    """Schema para resposta do health check.

    Attributes
    ----------
    status : str
        Status atual do serviço.
    timestamp : datetime
        Momento da verificação.
    version : str
        Versão do serviço.
    environment : str
        Ambiente de execução.
    uptime : float
        Tempo de atividade em segundos.

    """

    status: str
    timestamp: datetime
    version: str
    environment: str
    uptime: float
