"""
Configurações específicas para o modelo Gemini.
"""

from typing import Dict, Any

# Configurações do modelo
MODEL_CONFIG = {
    "name": "gemini-pro",
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "stop_sequences": [],
    "safety_settings": {
        "harassment": "block_none",
        "hate_speech": "block_none",
        "sexually_explicit": "block_none",
        "dangerous_content": "block_none"
    }
}

# Configurações de geração
GENERATION_CONFIG = {
    "temperature": MODEL_CONFIG["temperature"],
    "top_p": MODEL_CONFIG["top_p"],
    "top_k": MODEL_CONFIG["top_k"],
    "max_output_tokens": MODEL_CONFIG["max_output_tokens"],
    "stop_sequences": MODEL_CONFIG["stop_sequences"]
}

# Configurações de chamada
CALL_CONFIG = {
    "timeout": 30,
    "retry_count": 3,
    "backoff_factor": 1.5,
    "stream": False
}

# Configurações de prompt
PROMPT_CONFIG = {
    "system_prompt": """Você é um assistente especializado em análise e geração de código.
Suas principais capacidades incluem:
- Análise de código
- Sugestões de melhorias
- Documentação de código
- Resolução de problemas
- Boas práticas de programação

Por favor, forneça respostas claras e objetivas.""",
    "max_prompt_tokens": 30720,
    "token_limit_buffer": 1000
}

def get_model_config() -> Dict[str, Any]:
    """Retorna a configuração completa do modelo."""
    return {
        "model": MODEL_CONFIG,
        "generation": GENERATION_CONFIG,
        "call": CALL_CONFIG,
        "prompt": PROMPT_CONFIG
    }

def get_generation_config() -> Dict[str, Any]:
    """Retorna apenas as configurações de geração."""
    return GENERATION_CONFIG

def get_safety_settings() -> Dict[str, str]:
    """Retorna as configurações de segurança."""
    return MODEL_CONFIG["safety_settings"] 