"""
Implementação do serviço de sugestões do Cursor AI.
"""

from typing import Dict, Any, List
import logging

from ..interfaces import SuggestionInterface
from ..agent_services.embate_agent import EmbateSystem
from ...config.multiagent_config import GEMINI_CONFIG

logger = logging.getLogger(__name__)

class CursorAI(SuggestionInterface):
    """Implementação do Cursor AI usando sistema de embates."""
    
    def __init__(self):
        """Inicializa o serviço."""
        self.embate_system = EmbateSystem(config=GEMINI_CONFIG)
        self._capabilities = [
            'user_interaction',
            'code_analysis',
            'code_generation',
            'code_review',
            'documentation',
            'project_management'
        ]
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o contexto usando o sistema de embates."""
        try:
            # Extrai tarefa do contexto
            task = context.get("task") or context.get("prompt")
            if not task:
                raise ValueError("Contexto deve conter 'task' ou 'prompt'")
            
            # Processa com sistema de embates
            result = await self.embate_system.process_task(task, context)
            
            return {
                "status": "success",
                "result": result,
                "capabilities": self._capabilities
            }
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Gera uma sugestão usando o sistema de embates."""
        try:
            result = await self.embate_system.process_task(prompt, kwargs)
            
            # Pega resultado do sintetizador
            if "synthesizer" in result:
                return result["synthesizer"]
            
            # Ou combina todos os resultados
            return "\n".join(
                f"{agent}: {output}"
                for agent, output in result.items()
                if isinstance(output, str)
            )
            
        except Exception as e:
            logger.error(f"Erro na geração: {e}")
            return f"Erro ao gerar sugestão: {e}"
    
    def get_capabilities(self) -> List[str]:
        """Retorna as capacidades do serviço."""
        return self._capabilities.copy() 