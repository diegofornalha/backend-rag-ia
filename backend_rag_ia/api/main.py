"""
Aplicação principal da API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_rag_ia.services.llm_manager import LLMManager
from backend_rag_ia.api.middleware.multiagent_middleware import MultiAgentMiddleware
from backend_rag_ia.api.routes import health, documents
from backend_rag_ia.config.multiagent_config import MONITORING_CONFIG

# Inicialização do app
app = FastAPI(
    title="Backend RAG IA",
    description="API com suporte a RAG e sistema multiagente",
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

# Inicialização do LLM Manager com suporte multiagente
llm_manager = LLMManager()

# Adição do middleware multiagente
app.add_middleware(
    MultiAgentMiddleware,
    llm_manager=llm_manager
)

# Registro das rotas
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])

# Eventos do ciclo de vida
@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação."""
    if MONITORING_CONFIG["enable_logging"]:
        print("Sistema multiagente inicializado com sucesso!")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento da aplicação."""
    if MONITORING_CONFIG["enable_logging"]:
        print("Sistema multiagente finalizado com sucesso!") 