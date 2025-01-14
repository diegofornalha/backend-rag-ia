"""
Configuração das rotas da API.
"""

from fastapi import FastAPI
from backend_rag_ai_py.api.routes.document_routes import document_router
from backend_rag_ai_py.api.routes.chat_routes import chat_router

def configure_routes(app: FastAPI) -> None:
    """Configura todas as rotas da aplicação."""
    app.include_router(document_router)
    app.include_router(chat_router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}
