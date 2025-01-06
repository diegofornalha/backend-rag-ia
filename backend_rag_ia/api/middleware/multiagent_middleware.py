"""
Middleware para integração com o sistema multiagente.
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...config.settings import get_settings
from ...services.multiagent.core.coordinator import AgentCoordinator
from ...services.multiagent.core.providers import GeminiProvider


class MultiAgentMiddleware(BaseHTTPMiddleware):
    """Middleware para integração com o sistema multiagente."""

    def __init__(self, app: Callable):
        """
        Inicializa o middleware.

        Args:
            app: Aplicação FastAPI
        """
        super().__init__(app)

        # Configura provedor e coordenador
        settings = get_settings()
        provider = GeminiProvider(settings.GEMINI_API_KEY)
        self.coordinator = AgentCoordinator(provider)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Processa uma requisição.

        Args:
            request: Requisição HTTP
            call_next: Próximo handler

        Returns:
            Resposta HTTP
        """
        # Adiciona coordenador ao estado da requisição
        request.state.multiagent = self.coordinator

        # Continua processamento
        response = await call_next(request)
        return response
