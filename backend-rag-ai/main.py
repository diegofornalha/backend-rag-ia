"""
Arquivo principal da aplicação FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importar e configurar rotas após a criação do app
from backend_rag_ai_py.api.config_routes import configure_routes
from backend_rag_ai_py.middleware.error_handler import configure_error_handlers

app = FastAPI(
    title="Backend RAG AI",
    description="API com RAG e sistema multi-agente integrado",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Verifica se a aplicação está funcionando."""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Rota raiz da API."""
    return {
        "message": "Backend RAG AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online"
    }

# Configura rotas e handlers
configure_routes(app)
configure_error_handlers(app) 