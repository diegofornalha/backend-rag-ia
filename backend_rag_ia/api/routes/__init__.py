from .search import router as search_router
from .health import router as health_router
from .documents import router as documents_router
from .convert import router as convert_router

__all__ = [
    'search_router',
    'health_router',
    'documents_router',
    'convert_router'
] 