<<<<<<< Updated upstream
"""Implementa gerenciamento de comandos de embates.
=======
"""Módulo para gerenciamento de comandos de embates.
>>>>>>> Stashed changes

Este módulo fornece classes e funções para gerenciar comandos
executados durante os embates, incluindo registro e execução.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import click

from .models import Argumento, Embate
from .storage import SupabaseStorage


@click.group()
def cli():
    """Gerencia comandos para embates."""
    pass

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título do embate")
@click.option("--tipo", prompt="Tipo do embate", help="Tipo do embate")
@click.option("--contexto", prompt="Contexto", help="Contexto do embate")
async def criar(titulo: str, tipo: str, contexto: str):
    """Cria um novo embate."""
    embate = Embate(
        titulo=titulo,
        tipo=tipo,
        contexto=contexto,
        status="aberto",
        data_inicio=datetime.now()
    )

    storage = SupabaseStorage()
    result = await storage.save_embate(embate)

    click.echo(f"Embate criado: {result['data']['titulo']}")

@cli.command()
@click.argument("embate_id")
@click.option("--autor", prompt="Autor", help="Autor do argumento")
@click.option("--tipo", prompt="Tipo", help="Tipo do argumento")
@click.option("--conteudo", prompt="Conteúdo", help="Conteúdo do argumento")
async def argumentar(embate_id: str, autor: str, tipo: str, conteudo: str):
    """Adiciona um argumento a um embate."""
    storage = SupabaseStorage()

    # Busca embate
    embates = await storage.search_embates(embate_id)
    if not embates:
        click.echo("Embate não encontrado")
        return

    # Cria argumento
    argumento = Argumento(
        autor=autor,
        tipo=tipo,
        conteudo=conteudo,
        data=datetime.now()
    )

    # Atualiza embate
    embate = embates[0]
    embate["argumentos"].append(argumento.model_dump())

    result = await storage.update_embate(embate_id, {"argumentos": embate["argumentos"]})

    click.echo(f"Argumento adicionado ao embate: {result['data']['titulo']}")

@cli.command()
@click.argument("embate_id")
@click.option("--resolucao", prompt="Resolução", help="Resolução do embate")
async def resolver(embate_id: str, resolucao: str):
    """Resolve um embate."""
    storage = SupabaseStorage()

    updates = {
        "status": "resolvido",
        "resolucao": resolucao
    }

    result = await storage.update_embate(embate_id, updates)

    click.echo(f"Embate resolvido: {result['data']['titulo']}")

@cli.command()
@click.option("--query", help="Texto para buscar")
@click.option("--status", help="Status dos embates")
async def listar(query: str = None, status: str = None):
    """Lista embates."""
    storage = SupabaseStorage()

    if query:
        embates = await storage.search_embates(query)
    else:
        filters = {"status": status} if status else None
        embates = await storage.export_embates(filters)

    if not embates:
        click.echo("Nenhum embate encontrado")
        return

    for embate in embates:
        click.echo(f"\n{embate['titulo']}")
        click.echo(f"Status: {embate['status']}")
        click.echo(f"Tipo: {embate['tipo']}")
        click.echo(f"Data: {embate['data_inicio']}")

@dataclass
class Command:
<<<<<<< Updated upstream
    """Define um comando do embate.

=======
    """Representa um comando do embate.
    
>>>>>>> Stashed changes
    Attributes
    ----------
    name : str
        Nome do comando.
    args : dict[str, Any]
        Argumentos do comando.
    created_at : datetime
        Data e hora de criação.
    executed_at : Optional[datetime]
        Data e hora de execução.
    result : Optional[dict[str, Any]]
        Resultado da execução.
    error : Optional[str]
        Erro ocorrido durante a execução.
<<<<<<< Updated upstream

    """

=======
    """
>>>>>>> Stashed changes
    name: str
    args: dict[str, Any]
    created_at: datetime = datetime.now()
    executed_at: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    
    def execute(self) -> None:
        """Executa o comando.
        
        Raises
        ------
        Exception
            Se ocorrer algum erro durante a execução.
<<<<<<< Updated upstream

=======
>>>>>>> Stashed changes
        """
        try:
            # Implementação da execução
            self.executed_at = datetime.now()
        except Exception as err:
            self.error = str(err)
            raise

if __name__ == "__main__":
    cli()
