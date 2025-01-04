"""Módulo para configuração de rotas da API.

Este módulo fornece classes e funções para configurar as rotas
da API, incluindo configurações de CORS e middlewares.
"""

from typing import ClassVar


class CORSConfig:
    """Configuração de CORS para a API.

    Attributes
    ----------
    ALLOW_ORIGINS : list[str]
        Lista de origens permitidas.
    ALLOW_CREDENTIALS : bool
        Se credenciais são permitidas.
    ALLOW_METHODS : list[str]
        Lista de métodos HTTP permitidos.
    ALLOW_HEADERS : list[str]
        Lista de headers permitidos.

    """

    ALLOW_ORIGINS: ClassVar[list[str]] = ["*"]
    ALLOW_CREDENTIALS: ClassVar[bool] = True
    ALLOW_METHODS: ClassVar[list[str]] = ["*"]
    ALLOW_HEADERS: ClassVar[list[str]] = ["*"]


class RouteConfig:
    """Configuração de rotas da API.

    Attributes
    ----------
    PREFIX : str
        Prefixo para todas as rotas.
    TAGS : list[str]
        Tags para documentação da API.

    """

    PREFIX: ClassVar[str] = "/api/v1"
    TAGS: ClassVar[list[str]] = ["documents", "search", "statistics"]
