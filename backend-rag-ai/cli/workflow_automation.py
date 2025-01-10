import json
import os
import subprocess
from datetime import datetime
from typing import Optional

import click

from ..metrics.workflow_metrics import WorkflowMetrics
from ..notifications.notifier import EmbatesNotifier, FileHandler, LoggingHandler
from ..reports.report_generator import ReportGenerator
from ..storage.embates_storage import EmbatesStorage
from ..templates.embate_templates import EmbateTemplates


def run_git_command(command: str) -> tuple[int, str]:
    """Executa um comando git e retorna o código de saída e output"""
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return process.returncode, (output or error).decode()


@click.group()
def workflow():
    """Automação do fluxo de trabalho com embates"""
    pass


@workflow.command()
@click.option(
    "--tipo", type=click.Choice(["feature", "bug", "processo", "tech_debt"]), required=True
)
@click.option("--titulo", required=True)
@click.option("--contexto", required=True)
@click.option("--autor", required=True)
@click.option("--branch", help="Nome da branch para criar/usar")
@click.option("--commit-msg", help="Mensagem de commit personalizada")
def iniciar_fluxo(
    tipo: str,
    titulo: str,
    contexto: str,
    autor: str,
    branch: str | None = None,
    commit_msg: str | None = None,
):
    """Inicia um novo fluxo de trabalho com embate"""
    # 1. Cria/muda para branch se especificada
    if branch:
        # Verifica se branch existe
        code, _ = run_git_command(f"git checkout {branch}")
        if code != 0:
            # Cria nova branch
            code, output = run_git_command(f"git checkout -b {branch}")
            if code != 0:
                click.echo(f"Erro ao criar branch: {output}")
                return
            click.echo(f"Branch {branch} criada")
        click.echo(f"Usando branch: {branch}")

    # 2. Inicializa componentes
    storage = EmbatesStorage("dados/embates", "dados/backup")
    notifier = EmbatesNotifier()
    metrics = WorkflowMetrics()

    # Adiciona handlers de notificação
    notifier.add_handler(LoggingHandler())
    notifier.add_handler(FileHandler("dados/notificacoes"))

    # 3. Cria embate
    templates = EmbateTemplates()
    if tipo == "feature":
        embate = templates.create_feature_embate(titulo, contexto, autor)
    elif tipo == "bug":
        embate = templates.create_bug_embate(titulo, contexto, autor)
    elif tipo == "processo":
        embate = templates.create_process_embate(titulo, contexto, autor, "geral")
    else:  # tech_debt
        embate = templates.create_tech_debt_embate(titulo, contexto, autor, "geral")

    # 4. Salva embate
    embate_id = storage.save_embate(embate)
    click.echo(f"Embate criado: {embate_id}")

    # 5. Registra métricas
    metrics.record_operation(embate_id, "create")

    # 6. Gera relatórios
    generator = ReportGenerator(metrics, "dados/relatorios")
    generator.generate_all_reports()
    click.echo("Relatórios gerados em dados/relatorios/")

    # 7. Commit e push
    # Adiciona arquivos
    files_to_add = ["dados/embates/", "dados/notificacoes/", "dados/relatorios/", "backend_rag_ia/"]

    for file_path in files_to_add:
        if os.path.exists(file_path):
            code, output = run_git_command(f"git add {file_path}")
            if code != 0:
                click.echo(f"Erro ao adicionar {file_path}: {output}")

    # Faz commit
    msg = commit_msg or f"feat: {tipo} - {titulo}"
    code, output = run_git_command(f'git commit -m "{msg}"')
    if code != 0:
        click.echo(f"Erro ao fazer commit: {output}")
        return
    click.echo("Commit realizado")

    # Push
    if branch:
        code, output = run_git_command(f"git push origin {branch}")
    else:
        code, output = run_git_command("git push")

    if code != 0:
        click.echo(f"Erro ao fazer push: {output}")
        return
    click.echo("Push realizado com sucesso")


@workflow.command()
@click.argument("embate_id")
@click.option(
    "--novo_estado", type=click.Choice(["em_andamento", "bloqueado", "fechado"]), required=True
)
@click.option("--commit-msg", help="Mensagem de commit personalizada")
def atualizar_estado(embate_id: str, novo_estado: str, commit_msg: str | None = None):
    """Atualiza estado do embate e faz commit + push"""
    # 1. Carrega embate
    storage = EmbatesStorage("dados/embates", "dados/backup")
    embate = storage.load_embate(embate_id)
    if not embate:
        click.echo(f"Embate não encontrado: {embate_id}")
        return

    # 2. Atualiza estado
    old_state = embate["status"]
    embate["status"] = novo_estado
    storage.save_embate(embate)

    # 3. Registra métricas e notificações
    metrics = WorkflowMetrics()
    notifier = EmbatesNotifier()

    metrics.record_state_change(embate_id, old_state, novo_estado)
    notifier.notify_state_change(embate_id, old_state, novo_estado)

    # 4. Gera relatórios
    generator = ReportGenerator(metrics, "dados/relatorios")
    generator.generate_all_reports()

    # 5. Commit e push
    # Adiciona arquivos
    files_to_add = ["dados/embates/", "dados/notificacoes/", "dados/relatorios/"]

    for file_path in files_to_add:
        if os.path.exists(file_path):
            code, output = run_git_command(f"git add {file_path}")
            if code != 0:
                click.echo(f"Erro ao adicionar {file_path}: {output}")

    # Faz commit
    msg = commit_msg or f"chore: atualiza estado do embate {embate_id} para {novo_estado}"
    code, output = run_git_command(f'git commit -m "{msg}"')
    if code != 0:
        click.echo(f"Erro ao fazer commit: {output}")
        return
    click.echo("Commit realizado")

    # Push
    code, output = run_git_command("git push")
    if code != 0:
        click.echo(f"Erro ao fazer push: {output}")
        return
    click.echo("Push realizado com sucesso")


@workflow.command()
@click.option("--commit-msg", help="Mensagem de commit personalizada")
def gerar_relatorios(commit_msg: str | None = None):
    """Gera relatórios e faz commit + push"""
    # 1. Gera relatórios
    metrics = WorkflowMetrics()
    generator = ReportGenerator(metrics, "dados/relatorios")
    generator.generate_all_reports()
    click.echo("Relatórios gerados em dados/relatorios/")

    # 2. Commit e push
    code, output = run_git_command("git add dados/relatorios/")
    if code != 0:
        click.echo(f"Erro ao adicionar relatórios: {output}")
        return

    # Faz commit
    msg = commit_msg or "docs: atualiza relatórios de embates"
    code, output = run_git_command(f'git commit -m "{msg}"')
    if code != 0:
        click.echo(f"Erro ao fazer commit: {output}")
        return
    click.echo("Commit realizado")

    # Push
    code, output = run_git_command("git push")
    if code != 0:
        click.echo(f"Erro ao fazer push: {output}")
        return
    click.echo("Push realizado com sucesso")


if __name__ == "__main__":
    workflow()
