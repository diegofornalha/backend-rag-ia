"""
Módulo de serviços do backend.
"""

# Importações de interfaces
from .agent_services.coordinator import AgentCoordinator
from .embedding_services.vector_store import VectorStore
from .interfaces import SuggestionInterface
from .llm_services.providers.gemini import GeminiProvider

# Importações de implementações
from .suggestion_services.cursor_ai import CursorAI

__all__ = ["SuggestionInterface", "CursorAI", "AgentCoordinator", "GeminiProvider", "VectorStore"]
