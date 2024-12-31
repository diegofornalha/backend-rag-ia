#!/usr/bin/env python3
import json
import re
import subprocess
import time

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def get_build_status():
    try:
        # Verifica o status do builder
        builder_cmd = "docker buildx ls --format '{{json .}}'"
        builder_output = subprocess.check_output(builder_cmd, shell=True).decode()

        # Verifica containers em execução
        ps_cmd = "docker ps --format '{{json .}}'"
        ps_output = subprocess.check_output(ps_cmd, shell=True).decode()

        # Verifica logs do build atual
        build_cmd = (
            "docker buildx build . --progress=plain 2>&1 | grep -A 5 'Building.*26/27'"
        )
        try:
            build_output = subprocess.check_output(build_cmd, shell=True).decode()
        except subprocess.SubprocessError as e:
            build_output = f"Erro ao executar comando: {e}"

        builders = [
            json.loads(line) for line in builder_output.splitlines() if line.strip()
        ]
        containers = [
            json.loads(line) for line in ps_output.splitlines() if line.strip()
        ]

        return builders, containers, build_output
    except Exception as e:
        console.print(f"[red]Erro ao obter status: {e!s}[/red]")
        return [], [], ""


def parse_build_progress(build_output):
    progress_table = Table(title="Progresso do Build Atual (26/27)")
    progress_table.add_column("Etapa", style="cyan")
    progress_table.add_column("Tempo", style="yellow")
    progress_table.add_column("Status", style="green")

    # Extrai informações do build atual
    for line in build_output.splitlines():
        if "Building" in line and "(26/27)" in line:
            match = re.search(r"Building (\d+\.\d+)s \(26/27\) (.*)", line)
            if match:
                time_taken, step = match.groups()
                progress_table.add_row(step, f"{time_taken}s", "🔄 Em andamento")

    if build_output.strip():
        console.print(progress_table)


def show_build_info(builders, containers, build_output):
    # Mostra informações dos builders
    builder_table = Table(title="Docker Builders")
    builder_table.add_column("Nome", style="cyan")
    builder_table.add_column("Status", style="green")
    builder_table.add_column("Driver", style="yellow")
    builder_table.add_column("Plataformas", style="magenta")

    for builder in builders:
        builder_table.add_row(
            builder.get("Name", "N/A"),
            "✅ Ativo" if "running" in str(builder) else "❌ Inativo",
            builder.get("Driver", "N/A"),
            str(builder.get("Platforms", "N/A")),
        )

    console.print(builder_table)

    # Mostra informações dos containers
    container_table = Table(title="Containers em Execução")
    container_table.add_column("ID", style="cyan")
    container_table.add_column("Imagem", style="green")
    container_table.add_column("Status", style="yellow")
    container_table.add_column("Portas", style="magenta")
    container_table.add_column("Criado", style="blue")

    for container in containers:
        container_table.add_row(
            container.get("ID", "")[:12],
            container.get("Image", "N/A"),
            container.get("Status", "N/A"),
            container.get("Ports", "N/A"),
            container.get("CreatedAt", "N/A"),
        )

    console.print(container_table)

    # Mostra progresso do build atual
    parse_build_progress(build_output)


def check_image_manifest():
    try:
        cmd = "docker manifest inspect fornalha/backend:latest"
        output = subprocess.check_output(cmd, shell=True).decode()
        manifest = json.loads(output)

        manifest_table = Table(title="Manifesto da Imagem")
        manifest_table.add_column("Arquitetura", style="cyan")
        manifest_table.add_column("OS", style="green")
        manifest_table.add_column("Variante", style="yellow")
        manifest_table.add_column("Tamanho", style="magenta")
        manifest_table.add_column("Digest", style="blue")

        total_size = 0
        for platform in manifest.get("manifests", []):
            platform_info = platform.get("platform", {})
            size = platform.get("size", 0)
            total_size += size

            manifest_table.add_row(
                platform_info.get("architecture", "N/A"),
                platform_info.get("os", "N/A"),
                platform_info.get("variant", "N/A"),
                f"{size / 1024 / 1024:.2f} MB",
                platform.get("digest", "N/A")[:16],
            )

        if total_size > 0:
            console.print(manifest_table)
            console.print(
                f"[green]Tamanho total: {total_size / 1024 / 1024:.2f} MB[/green]"
            )
            return True
        return False
    except Exception:
        return False


def main():
    console.print(Panel.fit("🐳 Monitoramento de Build Docker", style="bold blue"))
    start_time = time.time()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("[cyan]Monitorando build (26/27)...", total=None)

        while True:
            console.clear()
            console.print(
                Panel.fit("🐳 Monitoramento de Build Docker", style="bold blue")
            )

            # Mostra tempo decorrido
            elapsed = time.time() - start_time
            console.print(
                f"[yellow]Tempo decorrido: {int(elapsed // 60)}m {int(elapsed % 60)}s[/yellow]"
            )

            builders, containers, build_output = get_build_status()
            show_build_info(builders, containers, build_output)

            # Verifica se a imagem está pronta
            if check_image_manifest():
                console.print(
                    "\n[green]✅ Build concluído! Imagem multi-plataforma está pronta.[/green]"
                )
                break

            time.sleep(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoramento interrompido pelo usuário[/yellow]")
