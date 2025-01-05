"""
Sistema MultiAgente integrado ao backend_rag_ia.

Este módulo implementa a integração do sistema multiagente com o backend principal.
"""

import os
from typing import Optional, Dict, Any

from .llm_services.providers.gemini import GeminiProvider
from .agent_services.coordinator import AgentCoordinator
from .llm_services.tracker import LlmTracker
from .suggestion_services.interfaces import CursorAI

class MultiAgentSystem:
    """Sistema MultiAgente integrado."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa o sistema multiagente."""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("API key do Gemini não encontrada")
            
        # Inicializa componentes
        self.provider = GeminiProvider(api_key=self.api_key)
        self.coordinator = AgentCoordinator()
        self.tracker = LlmTracker()
        
        # Registra agentes padrão
        self._register_default_agents()
    
    def _register_default_agents(self) -> None:
        """Registra os agentes padrão do sistema."""
        cursor_ai = CursorAI()
        
        for capability in cursor_ai._capabilities:
            self.coordinator.register_agent(capability, cursor_ai)
    
    async def process_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa uma tarefa usando o sistema multiagente."""
        try:
            full_context = {
                "task": task,
                "model": self.provider,
                "tracker": self.tracker
            }
            
            if context:
                full_context.update(context)
            
            return await self.coordinator.process(full_context)
            
        except Exception as e:
            self.tracker.track_event("system_error", {"error": str(e)})
            raise
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gera uma resposta usando o sistema multiagente."""
        try:
            full_context = {
                "input_context": prompt,
                "model": self.provider,
                "tracker": self.tracker
            }
            
            if context:
                full_context.update(context)
            
            return await self.coordinator.generate(full_context)
            
        except Exception as e:
            self.tracker.track_event("system_error", {"error": str(e)})
            raise
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna o status atual do sistema."""
        return {
            "coordinator": self.coordinator.get_status(),
            "tracker": self.tracker.get_metrics(),
            "config": self.provider.get_config()
        } 