from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Callable
import time
import logging
from datetime import datetime
from ..config.settings import get_settings

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()

async def environment_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware para verificar e validar o ambiente de execução."""
    if settings.is_render_environment:
        # Adiciona headers específicos do Render
        response = await call_next(request)
        response.headers["X-Render-Environment"] = "true"
        response.headers["X-Operation-Mode"] = settings.OPERATION_MODE
        return response
    return await call_next(request)

async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware para logging de requisições e respostas."""
    start_time = time.time()
    
    # Log da requisição
    logger.info(
        f"Request: {request.method} {request.url} "
        f"Mode: {settings.OPERATION_MODE}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log da resposta
        logger.info(
            f"Response: status={response.status_code} "
            f"process_time={process_time:.3f}s "
            f"environment={'render' if settings.is_render_environment else 'local'}"
        )
        
        # Adiciona headers de performance e ambiente
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Environment"] = settings.ENVIRONMENT
        return response
        
    except Exception as e:
        # Log do erro
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "timestamp": datetime.utcnow().isoformat(),
                "path": str(request.url),
                "environment": settings.ENVIRONMENT
            }
        )

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler global para tratamento de erros."""
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "environment": settings.ENVIRONMENT,
            "operation_mode": settings.OPERATION_MODE
        }
    ) 