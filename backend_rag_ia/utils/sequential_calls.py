"""Módulo para gerenciamento de chamadas sequenciais.

Este módulo fornece classes e funções para gerenciar chamadas sequenciais,
incluindo configuração, monitoramento e controle de fluxo.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar


@dataclass
class SequentialCallsConfig:
    """Configuração para o gerenciador de chamadas sequenciais.
    
    Attributes
    ----------
    LIMITE_AVISO : int
        Limite para emissão de avisos.
    LIMITE_MAXIMO : int
        Limite máximo de chamadas permitidas.
    TEMPO_RESET : int
        Tempo em segundos para resetar contadores.
    STORAGE_PATH : str
        Caminho para armazenamento de dados.
    NIVEIS_ALERTA : list[int]
        Níveis para emissão de alertas.
    BACKUP_ENABLED : bool
        Se o backup está habilitado.
    MAX_BACKUP_FILES : int
        Número máximo de arquivos de backup.
    VERSION : str
        Versão do gerenciador.

    """

    LIMITE_AVISO: ClassVar[int] = 20
    LIMITE_MAXIMO: ClassVar[int] = 25
    TEMPO_RESET: ClassVar[int] = 300  # 5 min
    STORAGE_PATH: ClassVar[str] = '~/.rag_sequential_calls'
    NIVEIS_ALERTA: ClassVar[list[int]] = [10, 15, 20, 23]
    BACKUP_ENABLED: ClassVar[bool] = True
    MAX_BACKUP_FILES: ClassVar[int] = 5
    VERSION: ClassVar[str] = "2.0.0"


@dataclass
class SequentialCall:
    """Representa uma chamada sequencial.
    
    Attributes
    ----------
    id : str
        Identificador único da chamada.
    status : str
        Status atual da chamada.
    created_at : datetime
        Data e hora de criação.
    metadata : dict[str, Any]
        Metadados associados à chamada.
    errors : list[str]
        Lista de erros ocorridos.

    """

    id: str
    status: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
