"""Implementa gerenciamento de comandos de embates.

Este módulo fornece classes e funções para gerenciar comandos
relacionados aos embates, incluindo listagem, criação e resolução.
"""

from typing import Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Command:
    """Define um comando do embate.
    
    Attributes
    ----------
    name : str
        Nome do comando
    args : dict[str, Any] 
        Argumentos do comando
    error : Optional[str]
        Erro ocorrido durante a execução.

    """
    name: str
    args: dict[str, Any]
    error: Optional[str] = None
