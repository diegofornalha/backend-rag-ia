"""
Configurações do modelo Gemini.
"""

import os
from typing import Any, Dict

GENERATION_CONFIG = {"temperature": 0.7, "top_p": 0.95, "top_k": 40, "max_output_tokens": 2048}


def get_model_config() -> dict[str, Any]:
    """Retorna a configuração do modelo."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")

    return {"model": "gemini-pro", "api_key": api_key, "generation_config": GENERATION_CONFIG}
