"""
Aplicação principal do Oráculo.
"""

import logging
import os

from api.routes import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configuração de logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Oráculo API")

# Configuração CORS
origins = os.getenv("CORS_ORIGINS", "[]")
try:
    import json

    origins_list = json.loads(origins)
except json.JSONDecodeError:
    logger.warning(f"CORS_ORIGINS inválido: {origins}. Usando padrão ['*']")
    origins_list = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rota de health check
@app.get("/api/v1/health")
async def health_check() -> dict[str, str]:
    """Verifica a saúde da aplicação."""
    return {"status": "healthy", "message": "API está funcionando normalmente"}


# Tratamento global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções."""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor", "message": str(exc)},
    )


# Inclui as rotas da API
app.include_router(router, prefix="/api/v1")

# Log de inicialização
logger.info("Aplicação iniciada com sucesso")
