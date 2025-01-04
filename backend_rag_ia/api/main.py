"""Módulo principal da API.

Este módulo fornece a configuração e inicialização da aplicação FastAPI,
incluindo rotas, middlewares e configurações.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config_routes import CORSConfig, RouteConfig
from .middleware import add_error_handler
from .routes import documents, search, statistics


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI.

    Returns
    -------
    FastAPI
        Aplicação FastAPI configurada.

    """
    app = FastAPI(
        title="RAG IA API",
        description="API para busca semântica em documentos",
        version="1.0.0"
    )

    # Configuração CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORSConfig.ALLOW_ORIGINS,
        allow_credentials=CORSConfig.ALLOW_CREDENTIALS,
        allow_methods=CORSConfig.ALLOW_METHODS,
        allow_headers=CORSConfig.ALLOW_HEADERS
    )

    # Adiciona handler de erros
    add_error_handler(app)

    # Inclui rotas
    app.include_router(
        documents.router,
        prefix=RouteConfig.PREFIX,
        tags=RouteConfig.TAGS
    )
    app.include_router(
        search.router,
        prefix=RouteConfig.PREFIX,
        tags=RouteConfig.TAGS
    )
    app.include_router(
        statistics.router,
        prefix=RouteConfig.PREFIX,
        tags=RouteConfig.TAGS
    )

    return app
