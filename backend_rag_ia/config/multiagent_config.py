"""
Configurações do sistema multiagente.
"""

import os
from typing import Dict, Any

# Configurações do Gemini
GEMINI_CONFIG = {
    "model": "gemini-pro",
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,
    "timeout": 30,
    "api_key": os.getenv("GEMINI_API_KEY"),
}

# Configurações dos Agentes
AGENT_CONFIG = {
    "cursor_ai": {
        "name": "Cursor AI",
        "role": "primary",
        "capabilities": [
            "user_interaction",
            "code_analysis",
            "code_generation",
            "code_review",
            "documentation",
            "project_management",
        ],
        "priority": 1,
    },
    "code_analyzer": {
        "name": "Code Analyzer",
        "role": "specialist",
        "capabilities": [
            "static_analysis",
            "dependency_check",
            "security_audit",
            "performance_analysis",
        ],
        "priority": 2,
    },
    "doc_generator": {
        "name": "Doc Generator",
        "role": "specialist",
        "capabilities": [
            "documentation_generation",
            "api_documentation",
            "code_comments",
            "readme_generation",
        ],
        "priority": 3,
    },
}

# Configurações do Coordenador
COORDINATOR_CONFIG = {
    "max_concurrent_agents": 3,
    "timeout_per_agent": 15,
    "retry_attempts": 2,
    "backoff_factor": 1.5,
}

# Configurações de Monitoramento
MONITORING_CONFIG = {
    "enable_logging": True,
    "log_level": "INFO",
    "metrics_collection": True,
    "performance_tracking": True,
}


def get_agent_config(agent_name: str) -> Dict[str, Any]:
    """Retorna a configuração específica de um agente."""
    return AGENT_CONFIG.get(agent_name, {})
