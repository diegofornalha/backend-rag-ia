#!/usr/bin/env python3
import os
import requests
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import time
import subprocess

console = Console()

class RenderManager:
    def __init__(self):
        self.api_key = os.getenv('RENDER_API_KEY')
        self.service_id = os.getenv('RENDER_SERVICE_ID')
        self.base_url = "https://api.render.com/v1"
        
        if not self.api_key or not self.service_id:
            console.print("[red]❌ RENDER_API_KEY ou RENDER_SERVICE_ID não encontrados![/red]")
            console.print("Por favor, configure as variáveis de ambiente:")
            console.print("export RENDER_API_KEY='seu_api_key'")
            console.print("export RENDER_SERVICE_ID='seu_service_id'")
            exit(1)
    
    def _get_headers(self):
        return {
            "accept": "application/json",
            "authorization": f"Bearer {self.api_key}"
        }
    
    def get_service_status(self):
        url = f"{self.base_url}/services/{self.service_id}"
        response = requests.get(url, headers=self._get_headers())
        if response.status_code == 200:
            data = response.json()
            return data.get('serviceDetails', {}).get('status', 'Desconhecido')
        return "Erro ao obter status"
    
    def verificar_imagem_docker(self):
        console.print("\n[bold blue]🔍 Verificando imagem Docker...[/bold blue]")
        
        # Verificar manifesto da imagem
        comando = "docker manifest inspect fornalha/backend:latest"
        try:
            resultado = subprocess.check_output(comando, shell=True).decode()
            manifesto = json.loads(resultado)
            
            # Verificar se suporta linux/amd64 (que é o que o Render usa)
            for plataforma in manifesto.get('manifests', []):
                if plataforma.get('platform', {}).get('architecture') == 'amd64':
                    console.print("[green]✅ Imagem suporta linux/amd64 (compatível com Render)[/green]")
                    return True
            
            console.print("[red]❌ Imagem não tem suporte para linux/amd64[/red]")
            return False
        except:
            console.print("[yellow]⚠️ Não foi possível verificar o manifesto da imagem[/yellow]")
            return True  # Continuar mesmo assim
    
    def reiniciar_servidor(self):
        console.print("\n[bold blue]🔄 Reiniciando servidor no Render...[/bold blue]")
        
        # Verificar imagem antes de reiniciar
        if not self.verificar_imagem_docker():
            if not console.input("\n[yellow]Continuar mesmo assim? (s/N): [/yellow]").lower().startswith('s'):
                console.print("[yellow]Reinicialização cancelada pelo usuário[/yellow]")
                return False
        
        # Configurar variáveis de ambiente para o deploy
        env_vars = {
            "DOCKER_IMAGE": "fornalha/backend:latest",
            "DOCKER_PLATFORM": "linux/amd64"  # Forçar uso da plataforma correta
        }
        
        # Iniciar nova implantação
        url = f"{self.base_url}/services/{self.service_id}/deploys"
        payload = {"env": env_vars}
        response = requests.post(url, headers=self._get_headers(), json=payload)
        
        if response.status_code != 200:
            console.print("[red]❌ Erro ao iniciar reinicialização[/red]")
            return False
        
        deploy_id = response.json().get('id')
        
        # Monitorar progresso
        with Progress() as progress:
            task = progress.add_task("[cyan]Aguardando reinicialização...", total=None)
            
            while True:
                status_url = f"{self.base_url}/services/{self.service_id}/deploys/{deploy_id}"
                status_response = requests.get(status_url, headers=self._get_headers())
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status', '')
                    
                    if status == 'live':
                        console.print("[green]✅ Servidor reiniciado com sucesso![/green]")
                        break
                    elif status in ['failed', 'canceled']:
                        console.print("[red]❌ Falha na reinicialização[/red]")
                        console.print("\nVerificando logs do deploy...")
                        self.mostrar_logs_deploy(deploy_id)
                        break
                
                time.sleep(5)
                progress.update(task, advance=1)
        
        return True
    
    def mostrar_logs_deploy(self, deploy_id):
        url = f"{self.base_url}/services/{self.service_id}/deploys/{deploy_id}/logs"
        response = requests.get(url, headers=self._get_headers())
        
        if response.status_code == 200:
            logs = response.json().get('logs', '')
            console.print("\n[bold]Logs do Deploy:[/bold]")
            console.print(logs)
        else:
            console.print("[red]Não foi possível obter os logs do deploy[/red]")
    
    def mostrar_status(self):
        status = self.get_service_status()
        
        tabela = Table(title="Status do Servidor")
        tabela.add_column("Serviço", style="cyan")
        tabela.add_column("Status", style="green")
        
        emoji_status = "🟢" if status.lower() == "live" else "🔴"
        tabela.add_row("Render", f"{emoji_status} {status}")
        
        console.print(tabela)

def main():
    console.print(Panel.fit("🚀 Gerenciador do Servidor Render", style="bold blue"))
    
    manager = RenderManager()
    
    while True:
        console.print("\n[bold cyan]Opções:[/bold cyan]")
        console.print("1. Verificar status")
        console.print("2. Reiniciar servidor")
        console.print("3. Sair")
        
        opcao = input("\nEscolha uma opção (1-3): ")
        
        if opcao == "1":
            manager.mostrar_status()
        elif opcao == "2":
            manager.reiniciar_servidor()
        elif opcao == "3":
            console.print("[yellow]Encerrando...[/yellow]")
            break
        else:
            console.print("[red]Opção inválida![/red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Programa interrompido pelo usuário[/yellow]") 