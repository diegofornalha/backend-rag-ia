"""Modelos de dados para o sistema de embates.

Este módulo define os modelos de dados utilizados no sistema de embates,
incluindo argumentos e embates propriamente ditos.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Argumento(BaseModel):
    """Modelo para argumentos em um embate.

    Esta classe representa um argumento dentro de um embate,
    contendo informações sobre o autor, tipo e conteúdo.

    Attributes
    ----------
    autor : str
        Autor do argumento.
    tipo : str
        Tipo do argumento (técnico ou preferência).
    conteudo : str
        Conteúdo do argumento.
    data : datetime
        Data de criação do argumento.

    """

    autor: str = Field(..., description="Autor do argumento")
    tipo: str = Field(..., description="Tipo do argumento (técnico ou preferência)")
    conteudo: str = Field(..., description="Conteúdo do argumento")
    data: datetime = Field(default_factory=datetime.now, description="Data de criação")


class Embate(BaseModel):
    """Modelo para embates.

    Esta classe representa um embate no sistema, contendo todas as
    informações relevantes como título, tipo, contexto e argumentos.

    Attributes
    ----------
    titulo : str
        Título do embate.
    tipo : str
        Tipo do embate (técnico ou preferência).
    contexto : str
        Contexto que motivou o embate.
    status : str
        Status do embate (aberto ou resolvido).
    data_inicio : datetime
        Data de início do embate.
    data_resolucao : Optional[datetime]
        Data de resolução do embate.
    resolucao : Optional[str]
        Resolução do embate.
    argumentos : list[Argumento]
        Lista de argumentos do embate.
    metadata : dict
        Metadados adicionais do embate.
    version_key : Optional[str]
        Chave de versionamento do embate.

    """

    titulo: str = Field(..., description="Título do embate")
    tipo: str = Field(..., description="Tipo do embate (técnico ou preferência)")
    contexto: str = Field(..., description="Contexto que motivou o embate")
    status: str = Field(default="aberto", description="Status do embate (aberto ou resolvido)")
    data_inicio: datetime = Field(default_factory=datetime.now, description="Data de início")
    data_resolucao: Optional[datetime] = Field(None, description="Data de resolução")
    resolucao: Optional[str] = Field(None, description="Resolução do embate")
    argumentos: list[Argumento] = Field(default_factory=list, description="Lista de argumentos")
    metadata: dict = Field(default_factory=dict, description="Metadados adicionais")
    version_key: Optional[str] = Field(None, description="Chave de versionamento")
