"""API principal do Backend RAG IA."""

from fastapi import FastAPI, Request, HTTPException
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

# Middleware de validação de origem
@app.middleware("http")
async def validate_origin(request: Request, call_next):
    """
    Middleware para validar a origem das requisições.
    Bloqueia requisições de origens não permitidas.
    """
    origin = request.headers.get("origin")
    
    # Se não houver origem (ex: requisição direta), permite
    if not origin:
        return await call_next(request)
        
    # Verifica se a origem está na lista de permitidas
    if origin not in settings.cors_origins_list:
        return JSONResponse(
            status_code=403,
            content={"detail": "Origin not allowed"}
        )
        
    return await call_next(request)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Métodos específicos em vez de "*"
    allow_headers=["Authorization", "Content-Type"],  # Headers específicos em vez de "*"
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