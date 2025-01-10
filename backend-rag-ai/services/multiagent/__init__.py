"""
Sistema MultiAgente integrado ao backend_rag_ia.

Este módulo implementa um sistema multiagente usando o modelo Gemini.
"""

from typing import Any, Dict

__version__ = "1.0.0"


def get_version() -> dict[str, Any]:
    """Retorna informações sobre a versão do sistema."""
    return {
        "version": __version__,
        "name": "MultiAgent System",
        "description": "Sistema multiagente integrado ao backend RAG",
    }
