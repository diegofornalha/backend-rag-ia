"""
Módulo de serviços do backend.
"""

# Importações de interfaces
from .interfaces import SuggestionInterface

# Importações de implementações
from .suggestion_services.cursor_ai import CursorAI
from .agent_services.coordinator import AgentCoordinator
from .llm_services.providers.gemini import GeminiProvider
from .embedding_services.vector_store import VectorStore

__all__ = [
    'SuggestionInterface',
    'CursorAI',
    'AgentCoordinator',
    'GeminiProvider',
    'VectorStore'
] 