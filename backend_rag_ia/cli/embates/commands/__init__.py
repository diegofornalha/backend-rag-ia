"""Comandos CLI para o sistema de embates.

Este módulo fornece comandos de linha de comando para interagir
com o sistema de embates, permitindo criar, listar e visualizar embates.
"""

import click

from ..manager import EmbateManager
from ..models import Embate


@click.group()
def cli():
    """Comandos para gerenciar embates.

    Este grupo de comandos fornece funcionalidades para gerenciar
    embates através da linha de comando.
    """
    pass


@cli.command()
@click.option("--tipo", default="manual", help="Tipo do embate")
@click.option("--titulo", prompt="Título", help="Título do embate")
@click.option("--contexto", prompt="Contexto", help="Contexto do embate")
async def create(tipo: str, titulo: str, contexto: str):
    """Cria um novo embate.

    Parameters
    ----------
    tipo : str
        Tipo do embate (padrão: "manual").
    titulo : str
        Título do embate.
    contexto : str
        Contexto do embate.

    """
    manager = EmbateManager()

    embate = Embate(
        tipo=tipo,
        titulo=titulo,
        contexto=contexto
    )

    result = await manager.create_embate(embate)
    click.echo(f"Embate criado com ID: {result['data']['id']}")


@cli.command()
@click.argument("id")
async def show(id: str):
    """Mostra detalhes de um embate.

    Parameters
    ----------
    id : str
        ID do embate a ser mostrado.

    """
    manager = EmbateManager()
    embate = await manager.get_embate(id)

    if not embate:
        click.echo("Embate não encontrado")
        return

    click.echo(f"Título: {embate.titulo}")
    click.echo(f"Tipo: {embate.tipo}")
    click.echo(f"Contexto: {embate.contexto}")
    click.echo(f"Status: {embate.status}")
    click.echo(f"Criado em: {embate.criado_em}")

    if embate.argumentos:
        click.echo("\nArgumentos:")
        for arg in embate.argumentos:
            click.echo(f"- {arg.nome}: {arg.valor}")


@cli.command()
async def list():
    """Lista todos os embates.

    Returns
    -------
    None
        Imprime a lista de embates no console.

    """
    manager = EmbateManager()
    embates = await manager.list_embates()

    if not embates:
        click.echo("Nenhum embate encontrado")
        return

    for embate in embates:
        click.echo(f"{embate.id}: {embate.titulo} ({embate.status})")


if __name__ == "__main__":
    cli()
