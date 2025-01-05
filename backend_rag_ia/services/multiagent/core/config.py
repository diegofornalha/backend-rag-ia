"""
Configurações específicas do sistema multiagente.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from ....config.settings import get_settings

class AgentConfig(BaseModel):
    """Configurações de um agente."""
    max_retries: int = 3
    timeout: int = 30
    batch_size: int = 10

class LLMConfig(BaseModel):
    """Configurações do modelo de linguagem."""
    model: str = "gemini-pro"
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 0.9
    top_k: int = 40
    api_key: Optional[str] = None

class MultiAgentConfig(BaseModel):
    """Configurações do sistema multiagente."""
    agent: AgentConfig = AgentConfig()
    llm: LLMConfig = LLMConfig()
    tracking_enabled: bool = True
    log_level: str = "INFO"

def get_multiagent_config() -> MultiAgentConfig:
    """
    Retorna as configurações do sistema multiagente.
    Combina configurações do settings.py com defaults.
    """
    settings = get_settings()
    
    # Pega configurações do settings.py
    config_dict = {
        "agent": settings.AGENT_CONFIG,
        "llm": {
            **settings.LLM_CONFIG,
            "api_key": settings.MULTIAGENT_CONFIG.get("gemini_api_key")
        },
        **settings.MULTIAGENT_CONFIG
    }
    
    return MultiAgentConfig(**config_dict)

def update_config(updates: Dict[str, Any]) -> None:
    """
    Atualiza configurações em runtime.
    Útil para testes e ajustes dinâmicos.
    """
    config = get_multiagent_config()
    
    for key, value in updates.items():
        if hasattr(config, key):
            setattr(config, key, value)
            
    return config 