"""Módulo para rotas de estatísticas da API.

Este módulo fornece endpoints para obter estatísticas do sistema,
incluindo métricas de uso e performance.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ...services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["statistics"])


class SystemStats(BaseModel):
    """Estatísticas do sistema.

    Attributes
    ----------
    total_documents : int
        Total de documentos armazenados.
    total_searches : int
        Total de buscas realizadas.
    avg_search_time : float
        Tempo médio de busca em segundos.
    uptime : float
        Tempo de atividade do sistema em segundos.

    """

    total_documents: int
    total_searches: int
    avg_search_time: float
    uptime: float


class SearchStats(BaseModel):
    """Estatísticas de busca.

    Attributes
    ----------
    total_queries : int
        Total de consultas realizadas.
    avg_results : float
        Média de resultados por busca.
    avg_score : float
        Pontuação média dos resultados.
    popular_terms : list[str]
        Termos mais buscados.

    """

    total_queries: int
    avg_results: float
    avg_score: float
    popular_terms: list[str]


class PerformanceStats(BaseModel):
    """Estatísticas de performance.

    Attributes
    ----------
    cpu_usage : float
        Uso de CPU em porcentagem.
    memory_usage : float
        Uso de memória em porcentagem.
    disk_usage : float
        Uso de disco em porcentagem.
    response_time : float
        Tempo médio de resposta em segundos.

    """

    cpu_usage: float
    memory_usage: float
    disk_usage: float
    response_time: float


@router.get("/system", response_model=SystemStats)
async def get_system_stats() -> SystemStats:
    """Obtém estatísticas gerais do sistema.

    Returns
    -------
    SystemStats
        Estatísticas do sistema.

    """
    service = StatisticsService()
    stats = await service.get_system_stats()
    return stats


@router.get("/search", response_model=SearchStats)
async def get_search_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> SearchStats:
    """Obtém estatísticas de busca.

    Parameters
    ----------
    start_date : Optional[datetime]
        Data inicial do período.
    end_date : Optional[datetime]
        Data final do período.

    Returns
    -------
    SearchStats
        Estatísticas de busca.

    """
    service = StatisticsService()
    stats = await service.get_search_stats(start_date, end_date)
    return stats


@router.get("/performance", response_model=PerformanceStats)
async def get_performance_stats() -> PerformanceStats:
    """Obtém estatísticas de performance.

    Returns
    -------
    PerformanceStats
        Estatísticas de performance.

    """
    service = StatisticsService()
    stats = await service.get_performance_stats()
    return stats
