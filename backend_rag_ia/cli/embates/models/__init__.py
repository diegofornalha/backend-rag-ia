"""Define modelos para embates.

Este módulo define as estruturas de dados básicas para o sistema de embates.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Argumento:
    """Define um argumento em um embate.

    Parameters
    ----------
    autor : str
        Nome ou identificador do autor do argumento.
    conteudo : str
        Conteúdo do argumento.
    tipo : str
        Tipo do argumento (ex: 'proposta', 'contra-argumento').
    data : datetime
        Data e hora em que o argumento foi criado.
    metadata : dict[str, Any]
        Metadados adicionais do argumento.
    """

    autor: str
    conteudo: str
    tipo: str
    data: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbateBase:
    """Define um embate base para análise de código.

    Parameters
    ----------
    titulo : str
        Título descritivo do embate.
    contexto : str
        Descrição detalhada do contexto do embate.
    tipo : str
        Tipo do embate (ex: 'refatoração', 'bug', 'feature').
    status : str
        Status atual do embate.
    data_inicio : datetime
        Data e hora de início do embate.
    data_resolucao : Optional[datetime]
        Data e hora de resolução do embate, se resolvido.
    argumentos : list[Argumento]
        Lista de argumentos do embate.
    decisao : Optional[str]
        Decisão final do embate, se houver.
    razao : Optional[str]
        Razão da decisão tomada.
    metadata : dict[str, Any]
        Metadados adicionais do embate.
    """

    titulo: str
    contexto: str
    tipo: str = "refatoracao"
    status: str = "aberto"
    data_inicio: datetime = field(default_factory=datetime.now)
    data_resolucao: Optional[datetime] = None
    argumentos: list[Argumento] = field(default_factory=list)
    decisao: Optional[str] = None
    razao: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
