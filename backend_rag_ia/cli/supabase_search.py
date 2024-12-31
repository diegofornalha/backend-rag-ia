#!/usr/bin/env python3

import configparser
import json
import os
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from supabase import Client, create_client

console = Console()

# Carrega variáveis de ambiente
load_dotenv()

# Configuração
config = configparser.ConfigParser()
config_path = Path.home() / ".config" / "supabase-cli" / "config.ini"


def load_config():
    """Carrega ou cria configuração."""
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config["DEFAULT"] = {
            "supabase_url": os.getenv("SUPABASE_URL", ""),
            "supabase_key": os.getenv("SUPABASE_KEY", ""),
            "cache_dir": str(Path.home() / ".cache" / "supabase-cli"),
            "max_results": "5",
        }
        with open(config_path, "w") as f:
            config.write(f)
    else:
        config.read(config_path)


def get_supabase_client() -> Client:
    """Cria cliente Supabase."""
    url = config["DEFAULT"]["supabase_url"]
    key = config["DEFAULT"]["supabase_key"]

    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser configurados!")

    return create_client(url, key)


def cache_results(query, results):
    """Cache local dos resultados."""
    cache_dir = Path(config["DEFAULT"]["cache_dir"])
    cache_dir.mkdir(parents=True, exist_ok=True)

    cache_file = cache_dir / f"{hash(query)}.json"
    with open(cache_file, "w") as f:
        json.dump(results, f)


def get_cached_results(query):
    """Recupera resultados do cache."""
    cache_file = Path(config["DEFAULT"]["cache_dir"]) / f"{hash(query)}.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)
    return None


@click.group()
def cli():
    """Cliente CLI para busca semântica no Supabase."""
    load_config()


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", default=None, help="Número máximo de resultados")
@click.option("--no-cache", is_flag=True, help="Ignora cache local")
def search(query, limit, no_cache):
    """Realiza busca semântica no Supabase."""
    if not no_cache:
        cached = get_cached_results(query)
        if cached:
            display_results(cached)
            return

    with Progress() as progress:
        task = progress.add_task("[cyan]Buscando no Supabase...", total=100)

        try:
            supabase = get_supabase_client()

            # Realiza a busca no Supabase
            response = supabase.rpc(
                "search_documents",
                {
                    "query_text": query,
                    "match_count": limit or int(config["DEFAULT"]["max_results"]),
                },
            ).execute()

            progress.update(task, completed=100)

            results = response.data

            if not no_cache:
                cache_results(query, results)

            display_results(results)

        except Exception as e:
            console.print(f"[red]Erro na busca: {e!s}")


def display_results(results):
    """Exibe resultados formatados."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Score", style="cyan", justify="right")
    table.add_column("Título", style="green")
    table.add_column("Conteúdo", style="white", width=60)

    for result in results:
        score = f"{result.get('similarity', 0):.2f}"
        title = result.get("metadata", {}).get("title", "Sem título")
        content = result.get("content", "")[:100] + "..."
        table.add_row(score, title, content)

    console.print(table)


@cli.command()
def show_config():
    """Mostra configuração atual."""
    for section in config.sections():
        click.echo(f"\n[{section}]")
        for key, value in config[section].items():
            click.echo(f"{key} = {value}")


if __name__ == "__main__":
    cli()
