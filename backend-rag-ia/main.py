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
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:10000",
    "https://localhost:10000",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://backend-rag-ia:8000",
    "https://backend-rag-ia:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=3600
)

# Inclui as rotas
app.include_router(rag_router, prefix="/api/v1", tags=["rag"])

@app.get("/")
async def root():
    """Redireciona para a documentação da API."""
    return RedirectResponse(url="/docs")

@app.get("/api/v1/health")
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