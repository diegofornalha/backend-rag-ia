"""
Gerenciador de modelos de linguagem com suporte a multiagentes.
"""

import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from MultiAgente_gemini.engine.llms.tracker import LlmTracker
from MultiAgente_gemini.analysis.suggestions.interfaces import CursorAI
from MultiAgente_gemini.engine.coordinator.base import AgentCoordinator

logger = logging.getLogger(__name__)

class LLMManager:
    """Gerenciador de modelos de linguagem com suporte a multiagentes."""
    
    def __init__(self):
        """Inicializa o gerenciador com suporte a multiagentes."""
        self.llm_tracker = LlmTracker()
        self.cursor_ai = CursorAI()
        self.coordinator = AgentCoordinator()
        self._setup_gemini()
    
    def _setup_gemini(self) -> None:
        """Configura o modelo Gemini."""
        try:
            genai.configure(timeout=30)  # Timeout em segundos
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as err:
            self.handle_error(err, "configuração do Gemini")
    
    def handle_error(self, error: Exception, context: str) -> None:
        """Trata erros de forma padronizada."""
        logger.error("Erro no processamento", extra={"context": context, "error": str(error)})
        if isinstance(error, ValueError):
            raise ValueError(f"Erro de valor no {context}") from error
        elif isinstance(error, ConnectionError):
            raise ConnectionError(f"Erro de conexão no {context}") from error
        else:
            raise RuntimeError(f"Erro inesperado no {context}") from error
    
    async def process_query(self, query: str) -> dict[str, str]:
        """Processa uma query usando o modelo e sistema multiagente."""
        try:
            # Processamento via multiagentes
            context = {
                "query": query,
                "model": self.model,
                "tracker": self.llm_tracker
            }
            
            # Análise inicial pelo CursorAI
            cursor_analysis = self.cursor_ai.analyze(context)
            
            # Coordenação dos agentes
            result = await self.coordinator.process(
                context=context,
                initial_analysis=cursor_analysis
            )
            
            return {
                "status": "success", 
                "result": result,
                "agent_info": cursor_analysis.metadata
            }
            
        except Exception as err:
            self.handle_error(err, "processamento de query")
            return {"status": "error", "result": str(err)}
    
    async def generate_response(self, context: str) -> dict[str, str]:
        """Gera uma resposta baseada no contexto usando multiagentes."""
        try:
            # Preparação do contexto para os agentes
            agent_context = {
                "input_context": context,
                "model": self.model,
                "tracker": self.llm_tracker
            }
            
            # Processamento coordenado
            response = await self.coordinator.generate(
                context=agent_context
            )
            
            return {
                "status": "success", 
                "response": response,
                "agent_metrics": self.llm_tracker.get_metrics()
            }
            
        except Exception as err:
            self.handle_error(err, "geração de resposta")
            return {"status": "error", "response": str(err)}
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retorna o status atual do sistema multiagente."""
        return {
            "cursor_ai": self.cursor_ai.name,
            "capabilities": self.cursor_ai._capabilities,
            "coordinator_status": self.coordinator.get_status(),
            "tracker_metrics": self.llm_tracker.get_metrics()
        } 