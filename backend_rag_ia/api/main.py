"""API principal do Backend RAG IA."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from .routes import (
    search_router,
    health_router,
    documents_router,
    statistics_router
)
from .middleware import (
    logging_middleware,
    error_handler,
    environment_middleware
)
from ..config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url=None  # Desabilitando ReDoc para evitar confusão
)

# Middlewares
app.middleware("http")(environment_middleware)
app.middleware("http")(logging_middleware)

# Handler global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return await error_handler(request, exc)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(documents_router, prefix="/api/v1", tags=["documents"])
app.include_router(statistics_router, prefix="/api/v1", tags=["statistics"])

# Rota raiz com redirecionamento para /docs
@app.get("/")
async def root():
    """Redireciona para a documentação da API."""
    return RedirectResponse(url="/docs") 