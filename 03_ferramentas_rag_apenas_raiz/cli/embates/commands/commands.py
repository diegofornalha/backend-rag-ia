"""
Comandos CLI para gerenciamento de embates.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Confirm

from backend_rag_ia.utils.logging_config import logger

from .manager import EmbateManager
from .models import Argumento, Embate

# Configura console
console = Console()

@click.group()
def cli():
    """CLI para gerenciamento de embates."""
    pass

@cli.command()
@click.argument('arquivo', type=click.Path(exists=True))
@click.option('--campo', help='Campo a ser editado')
@click.option('--valor', help='Novo valor para o campo')
@click.option('--excluir', is_flag=True, help='Exclui o embate')
async def edit(arquivo: str, campo: str | None, valor: str | None, excluir: bool):
    """Edita um embate existente."""
    try:
        if excluir:
            if Confirm.ask("Tem certeza que deseja excluir este embate?"):
                Path(arquivo).unlink()
                console.print("[green]Embate excluído com sucesso[/green]")
            return

        # Carrega embate
        with open(arquivo) as f:
            embate_data = json.load(f)
            
        if not campo or not valor:
            console.print("[red]Campo e valor são obrigatórios para edição[/red]")
            return
        
        # Valida campos
        campos_validos = {
            "titulo": str,
            "tipo": lambda x: x in ["tecnico", "preferencia"],
            "contexto": str,
            "status": lambda x: x in ["aberto", "resolvido"]
        }
        
        if campo not in campos_validos:
            console.print(f"[red]Campo inválido. Campos válidos: {', '.join(campos_validos.keys())}[/red]")
            return
        
        # Valida valor
        validator = campos_validos[campo]
        if isinstance(validator, type):
            try:
                valor = validator(valor)
            except ValueError:
                console.print(f"[red]Valor inválido para o campo {campo}[/red]")
                return
        elif not validator(valor):
            if campo == "tipo":
                console.print("[red]Tipo inválido. Use 'tecnico' ou 'preferencia'[/red]")
            elif campo == "status":
                console.print("[red]Status inválido. Use 'aberto' ou 'resolvido'[/red]")
            return
        
        # Verifica se o valor é diferente do atual
        if campo in embate_data and embate_data[campo] == valor:
            console.print("[yellow]O valor fornecido é igual ao valor atual[/yellow]")
            return
        
        # Atualiza embate
        manager = EmbateManager()
        updates = {campo: valor}
        await manager.update_embate(Path(arquivo).stem, updates)
        
        console.print("[green]Embate atualizado com sucesso[/green]")
        
    except Exception as e:
        logger.error(
            "Erro ao editar embate",
            extra={"error": str(e), "arquivo": arquivo},
            exc_info=True
        )
        console.print(f"[red]Erro ao editar embate: {e!s}[/red]")

@cli.command()
@click.option('--texto', help='Texto para buscar')
@click.option('--tag', help='Tag para filtrar')
async def search(texto: str | None, tag: str | None):
    """Busca embates."""
    try:
        with Progress() as progress:
            task = progress.add_task("Buscando...", total=100)
            
            # Prepara filtros
            filters: dict[str, Any] = {}
            if tag:
                filters["tags"] = [tag]
            
            # Busca embates
            manager = EmbateManager()
            results = await manager.search_embates(texto or "")
            
            progress.update(task, advance=100)
        
        if not results:
            console.print("[yellow]Nenhum resultado encontrado[/yellow]")
            return
        
        for result in results:
            console.print(f"\n[bold blue]{result['arquivo']}[/bold blue]")
            console.print(f"Título: {result['titulo']}")
            console.print(f"Tipo: {result['tipo']}")
            if "tags" in result.get("metadata", {}):
                console.print(f"Tags: {', '.join(result['metadata']['tags'])}")
            
    except Exception as e:
        logger.error(
            "Erro ao buscar embates",
            extra={"error": str(e)},
            exc_info=True
        )
        console.print(f"[red]Erro ao buscar embates: {e!s}[/red]")

@cli.command()
@click.argument('arquivo', type=click.Path(exists=True))
@click.option('--adicionar', help='Tag para adicionar')
@click.option('--remover', help='Tag para remover')
@click.option('--listar', is_flag=True, help='Lista as tags do embate')
async def tags(arquivo: str, adicionar: str | None, remover: str | None, listar: bool):
    """Gerencia tags de um embate."""
    try:
        # Carrega embate
        with open(arquivo) as f:
            data = json.load(f)
        
        if "metadata" not in data:
            data["metadata"] = {}
        if "tags" not in data["metadata"]:
            data["metadata"]["tags"] = []
        
        if listar:
            if data["metadata"]["tags"]:
                console.print("Tags:", ", ".join(data["metadata"]["tags"]))
            else:
                console.print("[yellow]Nenhuma tag encontrada[/yellow]")
            return
        
        # Atualiza tags
        updates: dict[str, Any] = {"metadata": data["metadata"]}
        if adicionar and adicionar not in data["metadata"]["tags"]:
            data["metadata"]["tags"].append(adicionar)
            console.print("[green]Tag adicionada com sucesso[/green]")
        
        if remover and remover in data["metadata"]["tags"]:
            data["metadata"]["tags"].remove(remover)
            console.print("[green]Tag removida com sucesso[/green]")
        
        # Atualiza embate
        manager = EmbateManager()
        await manager.update_embate(Path(arquivo).stem, updates)
        
    except Exception as e:
        logger.error(
            "Erro ao gerenciar tags",
            extra={"error": str(e), "arquivo": arquivo},
            exc_info=True
        )
        console.print(f"[red]Erro ao gerenciar tags: {e!s}[/red]")

@cli.command()
@click.argument('titulo')
@click.argument('tipo', type=click.Choice(['tecnico', 'preferencia']))
@click.argument('contexto')
@click.option('--autor', required=True, help='Autor do primeiro argumento')
@click.option('--argumento', required=True, help='Conteúdo do primeiro argumento')
async def create(titulo: str, tipo: str, contexto: str, autor: str, argumento: str):
    """Cria um novo embate."""
    try:
        # Cria embate
        embate = Embate(
            titulo=titulo,
            tipo=tipo,
            contexto=contexto,
            status="aberto",
            data_inicio=datetime.now(),
            argumentos=[
                Argumento(
                    autor=autor,
                    conteudo=argumento,
                    tipo=tipo,
                    data=datetime.now()
                )
            ],
            arquivo=f"embate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            version_key=f"{titulo.lower().replace(' ', '_')}_v1"
        )
        
        # Salva embate
        manager = EmbateManager()
        await manager.create_embate(embate)
        
        console.print("[green]Embate criado com sucesso[/green]")
        
    except Exception as e:
        logger.error(
            "Erro ao criar embate",
            extra={"error": str(e)},
            exc_info=True
        )
        console.print(f"[red]Erro ao criar embate: {e!s}[/red]")

if __name__ == "__main__":
    cli() 