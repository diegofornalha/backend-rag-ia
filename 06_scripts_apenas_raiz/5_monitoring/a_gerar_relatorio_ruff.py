#!/usr/bin/env python3
"""Script para gerar relatório de qualidade de código usando Ruff."""

import json
from collections import defaultdict

from rich.console import Console
from rich.table import Table

console = Console()

def carregar_violacoes(arquivo: str = "ruff_output.json") -> list[dict]:
    """Carrega as violações do arquivo JSON."""
    try:
        with open(arquivo) as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
        return []

def agrupar_por_tipo(violacoes: list[dict]) -> dict[str, list[dict]]:
    """Agrupa violações por tipo de regra."""
    grupos: defaultdict[str, list[dict]] = defaultdict(list)
    for v in violacoes:
        codigo = v.get("code", "Desconhecido")
        grupos[codigo].append(v)
    return dict(grupos)

def mostrar_estatisticas(violacoes: list[dict]) -> None:
    """Mostra estatísticas básicas das violações."""
    arquivos_afetados = {v.get("filename") for v in violacoes if v.get("filename")}
    grupos = agrupar_por_tipo(violacoes)

    table = Table(title="📈 Estatísticas")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="magenta")

    table.add_row("Total de Violações", str(len(violacoes)))
    table.add_row("Arquivos Afetados", str(len(arquivos_afetados)))
    table.add_row("Tipos de Regras", str(len(grupos)))

    console.print(table)

    # Top 5 regras mais violadas
    if grupos:
        table = Table(title="\n🎯 Top 5 Regras Mais Violadas")
        table.add_column("Regra", style="cyan")
        table.add_column("Ocorrências", style="magenta")
        table.add_column("Descrição", style="yellow")

        top_5 = sorted(grupos.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for regra, vs in top_5:
            desc = vs[0].get("message", "").split(":", 1)[-1].strip()
            table.add_row(regra, str(len(vs)), desc)

        console.print(table)

def mostrar_violacoes(violacoes: list[dict]) -> None:
    """Mostra detalhes das violações encontradas."""
    if not violacoes:
        console.print("[green]✨ Nenhuma violação encontrada![/green]")
        return

    # Agrupa por arquivo
    por_arquivo: defaultdict[str, list[dict]] = defaultdict(list)
    for v in violacoes:
        arquivo = v.get("filename", "Desconhecido")
        por_arquivo[arquivo].append(v)

    # Mostra violações por arquivo
    for arquivo, vs in por_arquivo.items():
        console.print(f"\n[cyan]📄 {arquivo}[/cyan]")
        for v in vs:
            linha = v.get("location", {}).get("row", "?")
            coluna = v.get("location", {}).get("column", "?")
            codigo = v.get("code", "?")
            msg = v.get("message", "Sem descrição")
            console.print(f"  [yellow]Linha {linha}:{coluna} - {codigo}[/yellow]: {msg}")

def main() -> None:
    """Função principal."""
    console.print("\n[bold blue]📊 Relatório de Qualidade de Código[/bold blue]\n")

    # Carrega violações
    violacoes = carregar_violacoes()

    # Mostra resultados
    mostrar_estatisticas(violacoes)
    mostrar_violacoes(violacoes)

if __name__ == "__main__":
    main()
