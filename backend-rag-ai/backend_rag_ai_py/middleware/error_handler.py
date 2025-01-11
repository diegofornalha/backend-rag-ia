"""
Configuração de tratamento de erros para a aplicação FastAPI.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

def configure_error_handlers(app: FastAPI):
    """Configura os handlers de erro da aplicação."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handler para erros de validação."""
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "body": exc.body
            }
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handler para exceções HTTP."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handler para exceções gerais."""
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "message": str(exc)
            }
        ) 