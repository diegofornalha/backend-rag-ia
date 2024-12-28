from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importa o router de Tools
from . import router as tools_router

# Cria a aplicação FastAPI
app = FastAPI(
    title="Tools API",
    description="API para ferramentas, utilitários e integrações diversas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui o router de Tools sem prefixo
app.include_router(tools_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 