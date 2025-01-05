"""
Base para os agentes do sistema.
"""

from typing import Dict, Any, Optional
import asyncio

from ..llm_services.tracker import LlmTracker
from ...analysis.suggestions.interfaces import CursorAI

class BaseAgent:
    """Classe base para agentes."""
    
    def __init__(self, tracker: Optional[LlmTracker] = None):
        """Inicializa o agente."""
        self.tracker = tracker or LlmTracker()
    
    async def process_with_timeout(self, task: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Processa uma tarefa com timeout.
        
        Args:
            task: Tarefa a ser processada
            timeout: Timeout em segundos
            
        Returns:
            Resultado do processamento
        """
        try:
            return await asyncio.wait_for(
                self.process(task),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            self.tracker.track_event("timeout", {"task": task})
            raise TimeoutError(f"Timeout ao processar tarefa: {task}")
    
    async def process_with_retry(
        self,
        task: str,
        max_retries: int = 3,
        delay: int = 1
    ) -> Dict[str, Any]:
        """
        Processa uma tarefa com retry.
        
        Args:
            task: Tarefa a ser processada
            max_retries: Número máximo de tentativas
            delay: Delay entre tentativas em segundos
            
        Returns:
            Resultado do processamento
        """
        for attempt in range(max_retries):
            try:
                return await self.process(task)
            except Exception as e:
                self.tracker.track_event("retry", {
                    "task": task,
                    "attempt": attempt + 1,
                    "error": str(e)
                })
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(delay * (attempt + 1))
    
    async def process(self, task: str) -> Dict[str, Any]:
        """
        Processa uma tarefa.
        
        Args:
            task: Tarefa a ser processada
            
        Returns:
            Resultado do processamento
        """
        raise NotImplementedError 