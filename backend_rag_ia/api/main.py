"""
Aplicação principal da API.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config_routes import configure_routes

# Configurações do ambiente
PORT = int(os.getenv("PORT", "10000"))
HOST = os.getenv("HOST", "0.0.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Cria aplicação
app = FastAPI(
    title="Backend RAG IA",
    description="API com RAG e sistema multi-agente integrado",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar rotas
configure_routes(app)


# Rota raiz
@app.get("/")
async def root():
    return {
        "name": "Backend RAG IA",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "online",
    }


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=HOST, port=PORT)
