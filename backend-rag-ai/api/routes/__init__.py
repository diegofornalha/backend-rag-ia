"""Routers da API."""

from .cache import router as cache_router
from .documents import router as documents_router
from .health import router as health_router
from .search import router as search_router
from .statistics import router as statistics_router

__all__ = [
    "search_router",
    "health_router",
    "documents_router",
    "statistics_router",
    "cache_router",
]
