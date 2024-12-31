from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routes import search
from .health import router as health_router
from .middleware import logging_middleware, error_handler, environment_middleware
from ..config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
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
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])

# Rota raiz
@app.get("/")
async def root():
    """Rota raiz da API."""
    return {
        "message": settings.API_TITLE,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "operation_mode": settings.OPERATION_MODE,
        "is_render": settings.is_render_environment,
        "active_url": settings.active_url,
        "docs_url": "/docs" if settings.DEBUG else None
    } 