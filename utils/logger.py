"""Módulo centralizado para logging da aplicação.

Este módulo fornece uma configuração centralizada para logging,
incluindo formatação consistente e rotação de arquivos.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Literal

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class LoggerConfig:
    """Configuração centralizada para logging."""
    
    def __init__(
        self,
        name: str,
        level: Union[LogLevel, str] = "INFO",
        log_file: Optional[Union[str, Path]] = None,
        max_bytes: int = 10_485_760,  # 10MB
        backup_count: int = 5,
        format_string: Optional[str] = None
    ) -> None:
        """Inicializa a configuração do logger.
        
        Args:
            name: Nome do logger
            level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Caminho para o arquivo de log (opcional)
            max_bytes: Tamanho máximo do arquivo de log antes da rotação
            backup_count: Número de arquivos de backup a manter
            format_string: String de formatação personalizada para as mensagens
        """
        self.name = name
        self.level = level
        self.log_file = Path(log_file) if log_file else None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.format_string = format_string or (
            "%(asctime)s | %(levelname)-8s | %(name)s | "
            "%(filename)s:%(lineno)d | %(message)s"
        )

def setup_logger(config: LoggerConfig) -> logging.Logger:
    """Configura e retorna um logger com as configurações especificadas.
    
    Args:
        config: Configuração do logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(config.name)
    logger.setLevel(config.level)
    
    # Remove handlers existentes para evitar duplicação
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter padrão
    formatter = logging.Formatter(config.format_string)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo (se especificado)
    if config.log_file:
        # Cria o diretório de logs se não existir
        os.makedirs(os.path.dirname(config.log_file), exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=config.log_file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger padrão da aplicação
default_logger = setup_logger(
    LoggerConfig(
        name="app",
        level="INFO",
        log_file="logs/app.log"
    )
)

def get_logger(
    name: str,
    level: Union[LogLevel, str] = "INFO",
    log_file: Optional[Union[str, Path]] = None
) -> logging.Logger:
    """Obtém um logger configurado com o nome especificado.
    
    Args:
        name: Nome do logger
        level: Nível de logging
        log_file: Caminho para o arquivo de log (opcional)
        
    Returns:
        Logger configurado
    """
    if log_file is None:
        log_file = f"logs/{name}.log"
    
    return setup_logger(
        LoggerConfig(
            name=name,
            level=level,
            log_file=log_file
        )
    ) 