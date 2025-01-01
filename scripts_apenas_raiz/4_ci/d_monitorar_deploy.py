import os
import time
from datetime import datetime

import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

console = Console()


def obter_status_deploy(service_id, api_key):
    """Obtém o status do deploy mais recente"""
    headers = {"Authorization": f"Bearer {api_key}"}
    url = f"https://api.render.com/v1/services/{service_id}/deploys?limit=1"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        deploys = response.json()

        if deploys and len(deploys) > 0:
            deploy = deploys[0]
            return {
                "status": deploy.get("status"),
                "finished_at": deploy.get("finishedAt"),
                "commit_message": deploy.get("commit", {}).get("message", "N/A"),
            }
    except Exception as e:
        console.print(f"[red]Erro ao verificar status: {e!s}[/red]")
    return None


def monitorar_deploy():
    """Monitora o status do deploy até completar"""
    service_id = os.getenv("RENDER_SERVICE_ID")
    api_key = os.getenv("RENDER_API_KEY")

    if not service_id or not api_key:
        console.print(
            "[red]Erro: RENDER_SERVICE_ID e RENDER_API_KEY precisam estar configurados[/red]"
        )
        return

    with Progress() as progress:
        task = progress.add_task("[cyan]Monitorando deploy...", total=None)

        while True:
            status_info = obter_status_deploy(service_id, api_key)

            if not status_info:
                time.sleep(10)
                continue

            status = status_info["status"]

            if status == "live":
                finished_at = status_info["finished_at"]
                commit_message = status_info["commit_message"]

                # Formata a data de conclusão
                if finished_at:
                    finished_time = datetime.fromisoformat(
                        finished_at.replace("Z", "+00:00")
                    )
                    finished_str = finished_time.strftime("%d/%m/%Y %H:%M:%S")
                else:
                    finished_str = "N/A"

                # Exibe mensagem de sucesso
                console.print("\n")
                console.print(
                    Panel.fit(
                        f"[green]✅ Deploy concluído com sucesso![/green]\n\n"
                        f"[white]Horário de conclusão:[/white] {finished_str}\n"
                        f"[white]Commit:[/white] {commit_message}",
                        title="Status do Deploy",
                        border_style="green",
                    )
                )
                break

            if status in ["failed", "canceled"]:
                console.print(
                    f"\n[red]❌ Deploy falhou ou foi cancelado. Status: {status}[/red]"
                )
                break

            progress.update(task, advance=1)
            time.sleep(10)


if __name__ == "__main__":
    monitorar_deploy()
