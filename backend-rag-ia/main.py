from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from api.routes import router as rag_router
import logging
import os
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Cria a aplicação FastAPI
app = FastAPI(
    title="backend-rag-ia",
    description="API para busca semântica e processamento de documentos",
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

# Inclui as rotas
app.include_router(rag_router, prefix="/api/v1", tags=["rag"])

@app.get("/")
async def root():
    """Redireciona para a documentação da API."""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Verifica o status da API."""
    try:
        return {
            "status": "healthy",
            "message": "API está funcionando normalmente"
        }
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return {
            "status": "unhealthy",
            "message": str(e)
        } 