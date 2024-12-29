from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as oraculo_router
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
    title="Oráculo API",
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
app.include_router(oraculo_router, prefix="/api/v1", tags=["oraculo"])

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