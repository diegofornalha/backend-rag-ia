"""
Aplicação principal da API.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .middleware import MultiAgentMiddleware
from .config_routes import configure_routes

# Configurações do ambiente
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Cria aplicação
app = FastAPI(
    title="Backend RAG IA",
    description="API para processamento de texto usando RAG e IA",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Adiciona middleware multiagente
app.add_middleware(MultiAgentMiddleware)

# Configura rotas
configure_routes(app)

# Rota de healthcheck
@app.get("/health")
async def health_check():
    """Verifica saúde da aplicação."""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT
    } 