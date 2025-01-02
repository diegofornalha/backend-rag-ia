"""Módulo principal para gerenciamento de embates."""

import click
from rich.progress import Progress
from rich.console import Console
from rich.prompt import Confirm
import json
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional
from datetime import datetime

@click.command()
@click.argument('arquivo', type=click.Path(exists=True))
@click.option('--campo', help='Campo a ser editado')
@click.option('--valor', help='Novo valor para o campo')
@click.option('--excluir', is_flag=True, help='Exclui o embate')
def edit_embate(arquivo: str, campo: str, valor: str, excluir: bool):
    """Edita um embate existente."""
    console = Console()
    
    if excluir:
        if Confirm.ask("Tem certeza que deseja excluir este embate?"):
            Path(arquivo).unlink()
            console.print("[green]Embate excluído com sucesso[/green]")
        return
    
    with open(arquivo) as f:
        data = json.load(f)
    
    campos_validos = {
        "titulo": str,
        "tipo": lambda x: x in ["tecnico", "preferencia"],
        "contexto": str,
        "status": lambda x: x in ["aberto", "resolvido"]
    }
    
    if campo not in campos_validos:
        console.print(f"[red]Campo inválido. Campos válidos: {', '.join(campos_validos.keys())}[/red]")
        return
    
    # Valida o valor
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
    
    data[campo] = valor
    
    with open(arquivo, "w") as f:
        json.dump(data, f, indent=2)
    
    console.print("[green]Embate atualizado com sucesso[/green]")

@click.command()
@click.option('--texto', help='Texto para buscar')
@click.option('--tag', help='Tag para filtrar')
@click.option('--dir', type=click.Path(exists=True), help='Diretório de busca')
def search_content(texto: Optional[str], tag: Optional[str], dir: str):
    """Busca conteúdo em embates."""
    console = Console()
    
    with Progress() as progress:
        task = progress.add_task("Buscando...", total=100)
        
        resultados = []
        dir_path = Path(dir)
        
        for arquivo in dir_path.glob("*.json"):
            with open(arquivo) as f:
                data = json.load(f)
            
            # Busca por tag
            if tag and "tags" in data:
                if tag not in data["tags"]:
                    continue
            
            # Busca por texto
            if texto:
                texto = texto.lower()
                conteudo = json.dumps(data, ensure_ascii=False).lower()
                if texto not in conteudo:
                    continue
            
            resultados.append((arquivo.name, data))
            progress.update(task, advance=100/len(list(dir_path.glob("*.json"))))
    
    if not resultados:
        console.print("[yellow]Nenhum resultado encontrado[/yellow]")
        return
    
    for nome, data in resultados:
        console.print(f"\n[bold blue]{nome}[/bold blue]")
        console.print(f"Título: {data['titulo']}")
        console.print(f"Tipo: {data['tipo']}")
        if "tags" in data:
            console.print(f"Tags: {', '.join(data['tags'])}")

@click.command()
@click.option('--dir-origem', type=click.Path(exists=True), help='Diretório de origem')
@click.option('--dir-destino', type=click.Path(exists=True), help='Diretório de destino')
@click.option('--tags', help='Tags para filtrar (separadas por vírgula)')
def export_embates(dir_origem: str, dir_destino: str, tags: Optional[str]):
    """Exporta embates para um arquivo zip."""
    console = Console()
    
    tags_list = tags.split(",") if tags else None
    
    with Progress() as progress:
        task = progress.add_task("Exportando...", total=100)
        
        export_file = Path(dir_destino) / "embates_export.zip"
        with zipfile.ZipFile(export_file, "w") as zf:
            dir_path = Path(dir_origem)
            total_files = len(list(dir_path.glob("*.json")))
            
            for i, arquivo in enumerate(dir_path.glob("*.json")):
                with open(arquivo) as f:
                    data = json.load(f)
                
                if tags_list and not (set(tags_list) & set(data.get("tags", []))):
                    continue
                
                zf.write(arquivo, arquivo.name)
                progress.update(task, advance=100/total_files)
    
    console.print("[green]Embates exportados com sucesso[/green]")

@click.command()
@click.option('--arquivo', type=click.Path(exists=True), help='Arquivo zip com embates')
@click.option('--dir-destino', type=click.Path(exists=True), help='Diretório de destino')
def import_embates(arquivo: str, dir_destino: str):
    """Importa embates de um arquivo zip."""
    console = Console()
    
    with Progress() as progress:
        task = progress.add_task("Importando...", total=100)
        
        with zipfile.ZipFile(arquivo) as zf:
            total_files = len(zf.namelist())
            
            for i, nome in enumerate(zf.namelist()):
                zf.extract(nome, dir_destino)
                progress.update(task, advance=100/total_files)
    
    console.print("[green]Embates importados com sucesso[/green]")

@click.command()
@click.argument('arquivo', type=click.Path(exists=True))
@click.option('--adicionar', help='Tag para adicionar')
@click.option('--remover', help='Tag para remover')
@click.option('--listar', is_flag=True, help='Lista as tags do embate')
def manage_tags(arquivo: str, adicionar: Optional[str], remover: Optional[str], listar: bool):
    """Gerencia tags de um embate."""
    console = Console()
    
    with open(arquivo) as f:
        data = json.load(f)
    
    if "tags" not in data:
        data["tags"] = []
    
    if listar:
        if data["tags"]:
            console.print("Tags:", ", ".join(data["tags"]))
        else:
            console.print("[yellow]Nenhuma tag encontrada[/yellow]")
        return
    
    if adicionar:
        if adicionar not in data["tags"]:
            data["tags"].append(adicionar)
            console.print("[green]Tag adicionada com sucesso[/green]")
    
    if remover:
        if remover in data["tags"]:
            data["tags"].remove(remover)
            console.print("[green]Tag removida com sucesso[/green]")
    
    with open(arquivo, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    cli = click.Group()
    cli.add_command(iniciar)
    cli.add_command(adicionar_argumento)
    cli.add_command(resolver)
    cli.add_command(listar)
    cli.add_command(edit_embate)
    cli.add_command(search_content)
    cli.add_command(export_embates)
    cli.add_command(import_embates)
    cli.add_command(manage_tags)
    cli() 