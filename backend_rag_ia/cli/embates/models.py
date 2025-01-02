"""
Modelos de dados para embates.
"""

from datetime import datetime


class Argumento:
    """Representa um argumento em um embate."""
    
    def __init__(
        self,
        autor: str,
        conteudo: str,
        tipo: str,
        data: datetime | None = None,
    ) -> None:
        """Inicializa um argumento."""
        self.autor = autor
        self.conteudo = conteudo
        self.tipo = tipo
        self.data = data or datetime.now()

class Embate:
    """Representa um embate."""
    
    def __init__(
        self,
        titulo: str,
        tipo: str,
        contexto: str,
        status: str,
        data_inicio: datetime | None = None,
        data_resolucao: datetime | None = None,
        argumentos: list[Argumento] | None = None,
        decisao: str | None = None,
        razao: str | None = None,
        arquivo: str | None = None,
        version_key: str | None = None,
        error_log: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        """Inicializa um embate."""
        self.titulo = titulo
        self.tipo = tipo
        self.contexto = contexto
        self.status = status
        self.data_inicio = data_inicio or datetime.now()
        self.data_resolucao = data_resolucao
        self.argumentos = argumentos or []
        self.decisao = decisao
        self.razao = razao
        self.arquivo = arquivo
        self.version_key = version_key
        self.error_log = error_log
        self.metadata = metadata or {} 