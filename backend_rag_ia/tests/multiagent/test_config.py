"""
Testes para as configurações do sistema multiagente.
"""

import pytest
from backend_rag_ia.services.multiagent.core.config import (
    get_multiagent_config,
    update_config,
    MultiAgentConfig
)

def test_default_config():
    """Testa se as configurações padrão são carregadas corretamente."""
    config = get_multiagent_config()
    
    assert isinstance(config, MultiAgentConfig)
    assert config.tracking_enabled is True
    assert config.log_level == "INFO"
    
    # Testa configurações do agente
    assert config.agent.max_retries == 3
    assert config.agent.timeout == 30
    assert config.agent.batch_size == 10
    
    # Testa configurações do LLM
    assert config.llm.model == "gemini-pro"
    assert 0 <= config.llm.temperature <= 1
    assert config.llm.max_tokens > 0

def test_config_update():
    """Testa a atualização de configurações em runtime."""
    updates = {
        "tracking_enabled": False,
        "log_level": "DEBUG"
    }
    
    config = update_config(updates)
    
    assert config.tracking_enabled is False
    assert config.log_level == "DEBUG"
    
    # Verifica se outros valores permanecem inalterados
    assert config.agent.max_retries == 3
    assert config.llm.model == "gemini-pro"

def test_invalid_config_update():
    """Testa tentativa de atualizar configuração inválida."""
    updates = {
        "invalid_key": "value"
    }
    
    config = update_config(updates)
    
    # Verifica se configuração permanece inalterada
    assert not hasattr(config, "invalid_key")
    assert config.tracking_enabled is True 