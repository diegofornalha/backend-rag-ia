#!/usr/bin/env python3
import click
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import os

REGISTRO_EMBATES = Path("dados/embates")
REGISTRO_EMBATES.mkdir(parents=True, exist_ok=True)

def salvar_embate(embate: Dict) -> None:
    """Salva o registro do embate em um arquivo JSON."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo = REGISTRO_EMBATES / f"embate_{timestamp}.json"
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(embate, f, ensure_ascii=False, indent=2)

def carregar_embates() -> List[Dict]:
    """Carrega todos os embates registrados."""
    embates = []
    for arquivo in REGISTRO_EMBATES.glob("embate_*.json"):
        with open(arquivo, encoding="utf-8") as f:
            embates.append(json.load(f))
    return embates

@click.group()
def cli():
    """Ferramenta para gerenciar embates saudáveis no projeto."""
    pass

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título descritivo do embate")
@click.option("--tipo", type=click.Choice(["preferencia", "tecnico"]), prompt="Tipo do embate")
@click.option("--contexto", prompt="Contexto do embate", help="Descrição detalhada do contexto")
def iniciar(titulo: str, tipo: str, contexto: str):
    """Inicia um novo embate."""
    embate = {
        "titulo": titulo,
        "tipo": tipo,
        "contexto": contexto,
        "status": "aberto",
        "data_inicio": datetime.now().isoformat(),
        "argumentos": [],
        "decisao": None,
        "razao": None
    }
    
    salvar_embate(embate)
    click.echo(f"\n✅ Embate iniciado: {titulo}")
    click.echo("\nPróximos passos:")
    click.echo("1. Use 'adicionar-argumento' para registrar argumentos")
    click.echo("2. Use 'resolver' quando chegar a uma conclusão")
    click.echo("3. Use 'listar' para ver todos os embates")

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título do embate para adicionar argumento")
@click.option("--autor", prompt="Autor do argumento", help="Quem está apresentando o argumento")
@click.option("--argumento", prompt="Argumento", help="O argumento em si")
@click.option("--tipo", type=click.Choice(["tecnico", "preferencia"]), prompt="Tipo do argumento")
def adicionar_argumento(titulo: str, autor: str, argumento: str, tipo: str):
    """Adiciona um argumento a um embate existente."""
    embates = carregar_embates()
    for embate in embates:
        if embate["titulo"] == titulo and embate["status"] == "aberto":
            novo_argumento = {
                "autor": autor,
                "conteudo": argumento,
                "tipo": tipo,
                "data": datetime.now().isoformat()
            }
            embate["argumentos"].append(novo_argumento)
            salvar_embate(embate)
            click.echo(f"\n✅ Argumento adicionado ao embate: {titulo}")
            return
    
    click.echo("❌ Embate não encontrado ou já fechado")

@cli.command()
@click.option("--titulo", prompt="Título do embate", help="Título do embate para resolver")
@click.option("--decisao", prompt="Decisão final", help="A decisão tomada")
@click.option("--razao", prompt="Razão da decisão", help="Justificativa da decisão")
def resolver(titulo: str, decisao: str, razao: str):
    """Resolve um embate existente."""
    embates = carregar_embates()
    for embate in embates:
        if embate["titulo"] == titulo and embate["status"] == "aberto":
            embate["status"] = "resolvido"
            embate["decisao"] = decisao
            embate["razao"] = razao
            embate["data_resolucao"] = datetime.now().isoformat()
            salvar_embate(embate)
            
            # Gerar registro no formato markdown
            registro_md = f"""## Decisão: {titulo}

- Tipo: {embate['tipo']}
- Contexto: {embate['contexto']}
- Data Início: {embate['data_inicio']}
- Data Resolução: {embate['data_resolucao']}

### Argumentos:

{chr(10).join([f"- **{arg['autor']}** ({arg['tipo']}): {arg['conteudo']}" for arg in embate['argumentos']])}

### Decisão Final
{decisao}

### Razão
{razao}
"""
            
            # Salvar no arquivo de registro de decisões
            registro_path = Path("01_regras_md_apenas_raiz/1_core/j_registro_decisoes.md")
            if registro_path.exists():
                with open(registro_path, "a", encoding="utf-8") as f:
                    f.write(f"\n\n{registro_md}")
            
            click.echo(f"\n✅ Embate resolvido: {titulo}")
            click.echo("\nRegistro adicionado ao arquivo de decisões")
            return
    
    click.echo("❌ Embate não encontrado ou já fechado")

@cli.command()
@click.option("--status", type=click.Choice(["aberto", "resolvido", "todos"]), default="todos", help="Filtrar por status")
def listar(status: str):
    """Lista todos os embates registrados."""
    embates = carregar_embates()
    
    if not embates:
        click.echo("Nenhum embate registrado")
        return
    
    for embate in embates:
        if status == "todos" or embate["status"] == status:
            click.echo(f"\n📌 {embate['titulo']}")
            click.echo(f"Status: {embate['status']}")
            click.echo(f"Tipo: {embate['tipo']}")
            click.echo(f"Contexto: {embate['contexto']}")
            if embate["argumentos"]:
                click.echo("\nArgumentos:")
                for arg in embate["argumentos"]:
                    click.echo(f"- {arg['autor']}: {arg['conteudo']} ({arg['tipo']})")
            if embate["status"] == "resolvido":
                click.echo(f"\nDecisão: {embate['decisao']}")
                click.echo(f"Razão: {embate['razao']}")
            click.echo("-" * 50)

if __name__ == "__main__":
    cli() 