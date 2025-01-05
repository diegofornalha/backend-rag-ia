"""
Middleware para integração do sistema multiagente.
"""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend_rag_ia.services.llm_manager import LLMManager
from backend_rag_ia.config.multiagent_config import MONITORING_CONFIG
import logging

logger = logging.getLogger(__name__)

class MultiAgentMiddleware(BaseHTTPMiddleware):
    """Middleware para integração do sistema multiagente."""
    
    def __init__(self, app, llm_manager: LLMManager):
        """Inicializa o middleware com o gerenciador LLM."""
        super().__init__(app)
        self.llm_manager = llm_manager
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura o logging do middleware."""
        if MONITORING_CONFIG["enable_logging"]:
            logging.basicConfig(
                level=MONITORING_CONFIG["log_level"],
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Processa a requisição através do sistema multiagente."""
        try:
            # Coleta informações do contexto
            context = {
                "path": request.url.path,
                "method": request.method,
                "headers": dict(request.headers),
                "query_params": dict(request.query_params)
            }
            
            # Análise do contexto pelos agentes
            agent_response = await self.llm_manager.process_query(
                str(context)
            )
            
            # Adiciona informações dos agentes ao request state
            request.state.agent_info = agent_response.get("agent_info", {})
            
            # Processa a requisição
            response = await call_next(request)
            
            # Gera resposta enriquecida pelos agentes
            if MONITORING_CONFIG["metrics_collection"]:
                agent_status = self.llm_manager.get_agent_status()
                response.headers["X-Agent-Metrics"] = str(agent_status)
            
            return response
            
        except Exception as e:
            logger.error(f"Erro no middleware multiagente: {str(e)}")
            return Response(
                content={"error": "Erro interno no processamento multiagente"},
                status_code=500
            ) 