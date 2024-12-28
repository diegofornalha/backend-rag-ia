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
from typing import Optional, Union, Literal, Any, TypeVar, cast, Dict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LoggerType = TypeVar('LoggerType', logging.Logger, logging.LoggerAdapter[logging.Logger])

class LoggerConfig:
    """Configuração centralizada para logging."""
    
    def __init__(
        self,
        name: str,
        level: Union[LogLevel, str] = "INFO",
        log_file: Optional[Union[str, Path]] = None,
        max_bytes: int = 10_485_760,  # 10MB
        backup_count: int = 5,
        format_string: Optional[str] = None,
        rag_debug: bool = False,
        extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """Inicializa a configuração do logger.
        
        Args:
            name: Nome do logger
            level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Caminho para o arquivo de log (opcional)
            max_bytes: Tamanho máximo do arquivo de log antes da rotação
            backup_count: Número de arquivos de backup a manter
            format_string: String de formatação personalizada para as mensagens
            rag_debug: Se True, habilita logging detalhado para operações RAG
            extra: Campos extras para o LoggerAdapter
        """
        self.name = name
        self.level = level
        self.log_file = Path(log_file) if log_file else None
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.rag_debug = rag_debug
        self.extra = extra or {}
        
        # Formato especial para debug RAG se habilitado
        if rag_debug and not format_string:
            self.format_string = (
                "%(asctime)s | %(levelname)-8s | RAG | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s | "
                "vector_dim=%(vector_dim)s | chunk_size=%(chunk_size)s"
            )
        else:
            self.format_string = format_string or (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(filename)s:%(lineno)d | %(message)s"
            )

def setup_logger(config: LoggerConfig) -> LoggerType:
    """Configura e retorna um logger com as configurações especificadas.
    
    Args:
        config: Configuração do logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(config.name)
    logger.setLevel(config.level)
    
    # Limpa handlers existentes
    logger.handlers = []
    
    # Configura o formatter
    formatter = logging.Formatter(config.format_string)
    
    # Adiciona handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Adiciona handler para arquivo se especificado
    if config.log_file:
        # Cria diretório para logs se não existir
        config.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            str(config.log_file),
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Adiciona contexto extra para RAG se debug estiver habilitado
    if config.rag_debug:
        extra = {
            'vector_dim': 'N/A',
            'chunk_size': 'N/A',
            **config.extra
        }
        return cast(LoggerType, logging.LoggerAdapter(logger, extra=extra))

    return cast(LoggerType, logger)

def get_logger(
    name: str,
    level: Union[LogLevel, str] = "INFO",
    log_file: Optional[Union[str, Path]] = None,
    rag_debug: bool = False,
    extra: Optional[Dict[str, Any]] = None
) -> LoggerType:
    """Obtém um logger configurado com o nome especificado.
    
    Args:
        name: Nome do logger
        level: Nível de logging
        log_file: Caminho para o arquivo de log (opcional)
        rag_debug: Se True, habilita logging detalhado para operações RAG
        extra: Campos extras para o LoggerAdapter
        
    Returns:
        Logger configurado
    """
    if log_file is None:
        log_file = f"logs/{name}.log"
    
    return setup_logger(
        LoggerConfig(
            name=name,
            level=level,
            log_file=log_file,
            rag_debug=rag_debug,
            extra=extra
        )
    )

# Logger padrão da aplicação
default_logger = setup_logger(
    LoggerConfig(
        name="app",
        level="INFO",
        log_file="logs/app.log"
    )
) 