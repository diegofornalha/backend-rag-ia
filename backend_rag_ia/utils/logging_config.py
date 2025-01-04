"""Configuração de logging para o projeto."""

import logging


def setup_logging() -> logging.Logger:
    """Configura o sistema de logging."""
    # Configurar logger
    logger = logging.getLogger("backend_rag_ia")
    logger.setLevel(logging.INFO)
    
    # Configurar formato do log
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Configurar handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Criar instância global do logger
logger = setup_logging()
