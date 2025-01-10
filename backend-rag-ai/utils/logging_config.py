"""
Configuração de logging para o sistema.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str, level: str | None = None, format_str: str | None = None
) -> logging.Logger:
    """
    Configura um logger com formatação padrão.

    Args:
        name: Nome do logger
        level: Nível de logging opcional
        format_str: String de formatação opcional

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Define nível
    logger.setLevel(level or "INFO")

    # Adiciona handler se não existir
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level or "INFO")

        # Define formatação
        formatter = logging.Formatter(
            format_str or "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

    return logger


# Criar instância global do logger
logger = setup_logger("backend_rag_ia")
