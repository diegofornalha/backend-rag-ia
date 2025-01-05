"""
Configuração de logging para o sistema multiagente.
"""

import logging
from typing import Optional
from ....utils.logging_config import setup_logger

def get_multiagent_logger(
    name: str,
    level: Optional[str] = None
) -> logging.Logger:
    """
    Retorna um logger configurado para o sistema multiagente.
    
    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de logging opcional (DEBUG, INFO, etc)
        
    Returns:
        Logger configurado
    """
    logger = setup_logger(
        name=f"multiagent.{name}",
        level=level or "INFO"
    )
    
    # Adiciona formatação específica para multiagent
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s [MultiAgent:%(name)s] %(message)s'
    )
    
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    
    return logger 